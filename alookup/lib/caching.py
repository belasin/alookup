"""Caching for google wifi access point geolocation requests

Example:
    from alookup.lib.caching import GoogleGeocodeCache as cache

    ...

    @cache
    def function_that_needs_caching(apscan, ...):
        #Do your stuff
        ...
        return output

    #Don't forget to set it up when you init caching using config.include
    def main(global_config, **settings):
        with Configurator(settings=settings) as config:
            #Set up Caching
            config.include('.lib.caching')

This module implements
 - Backend Support
  - DictBackend [in memory]
  - RedisBackend *TODO
 - Indexed Access Point approximation for fast caching

Attributes:
    backend_urn_re (re): Regular expression for matching the backends
    log (logging): Logger instance for logging for this module

Todo:
 - RedisBackend needs to be implemented
 - TTL Cache invalidation needs to be created
"""
from functools import update_wrapper
from pyramid.threadlocal import get_current_registry
from pyramid.settings import asbool
from math import ceil
import uuid
import re
import logging

log = logging.getLogger("alookup.caching")


class DictBackend(object):

    """Implements an in memory dictionary backend for use in caching
    """
    
    def __init__(self, cnf=None):
        """Initialize the data memory storage
        """
        log.info("Caching started with DictBackend")
        self.data = {}

    def flush(self):
        """Empty the storage backend of all it's cached entries
        """
        self.data = {}

    def setkey(self, key, value):
        """Set the value for a specific key
        
        Args:
            key (str): Key to update the value
            value (*): Value to set
        """
        self.data[key] = value

    def appendkey(self, key, value):
        """Addes the value to the value at the key

        This assumes the value is part of a list so it will always append it to the list, 
        if the key does not exist it will create the list with the value as the only item in
        that list
        
        Args:
            key (str: Key for the list
            value (*): Value to add to the list
        
        Raises:
            TypeError: If the key exists in the backend but the value is not a list it will raise a TypeError
        """
        if key in self.data:
            if type(self.data[key]) != list:
                raise TypeError("Data type is not a list")
            else:
                self.data[key].append(value)
        else:
            self.data[key] = [value]

    def getkey(self, key):
        """Get the value at a specific key
        
        Args:
            key (str): Key to get the value
        
        Returns:
            *: Value at the key
        """
        return self.data.get(key)

    def iskey(self, key):
        """Tests if the key exists in the backend
        
        Args:
            key (str): Key to test
        
        Returns:
            boolean: If the key exists then we return True
        """
        return key in self.data

class RedisBackend(object):
    """Implements the RedisBackend

    On a distributed production environment it is useful to have a transient caching system

    i.e. Multiple separate instances of the application can be run and 
    share the same cache backend across all of them, this means that on high volume
    systems you get the caching benefit of all of these

    TODO:
     - Implement this backend

    """
    
    def __init__(self, cnf):
        raise NotImplemented("Definately can be done if you wanted to scale the system")

backend_urn_re = re.compile("^(dict|redis\:\/\/(.*){3,5})$")

_backends = {
    "dict": DictBackend,
    "redis": RedisBackend
}

class GoogleGeocodeCache(object):

    """Cache Decorator is used to cleanly apply the caching
    
    Attributes:
        backend (backend): Instance of the active backend
        depth (int): How many access point cache entries will we search through before we give up
        func (func): Decorated function
        is_enabled (bool): Is caching enabled
        match_required (int): Percentage of the match that is required to consider them the same
        signal_bands (dict): Dictionary lookup to group signals into sets (bands)
    """
    
    is_enabled = False

    backend = None

    depth = 6

    match_required = 80

    signal_bands = {
        40: "A",
        50: "B",
        60: "C",
        70: "D",
        80: "E",
        9999: "F"
    }

    def __init__(self, func):
        """When we decorate a function it inits the class which replaces the decorated function
        
        Args:
            func (func): Decorated function
        """
        update_wrapper(self, func)
        self.func = func

    def generate_cache_key(self, ent):
        """Takes an apscan entry and determines a backend key

        <SSID:MACADDRESS>::<Signal Band>
        
        Args:
            ent (dict): Apscan entry
        
        Returns:
            str: Key derived from the access point information
        """
        k = [i for i in sorted(self.signal_bands.keys()) if i >= -ent["signalStrength"]][0]
        sband = self.signal_bands[k]
        return "%s::%s" % (ent["macAddress"], sband)

    def save(self, apscan, result):
        """Cache the result
        
        Args:
            apscan (list): List of access point scan entries
            result (dict): The result of executing the decorated self.func
        """
        apscan = sorted(apscan, key=lambda x:x["signalStrength"], reverse=True)
        _id = str(uuid.uuid4())
        _keylist = []
        for ent in apscan:
            k = self.generate_cache_key(ent)
            self.backend.appendkey(k, _id)
            _keylist.append(k)
        _data = {
            "request": apscan,
            "result": result,
            "keylist": _keylist
        }
        self.backend.setkey(_id, _data)

    def lookup(self, apscan):
        """Attempts to lookup the apscan entries to see if a cached entry exists
        
        Args:
            apscan (list): List of access points scan entries
        
        Returns:
            dict(nullable): If we can find the cache entry we return it otherwise null is returned
        """
        apscan = sorted(apscan, key=lambda x:x["signalStrength"], reverse=True)
        _ent_cnt = len(apscan)
        _uuid_list = []

        _keys = [self.generate_cache_key(ent)for ent in apscan]
        for k in _keys:
            _uuid_res = self.backend.getkey(k)
            if _uuid_res:
                _uuid_list += _uuid_res
        uuid_cnts = dict((i,1) for i in _uuid_list)
        for key in uuid_cnts:
            uuid_cnts[key] = _uuid_list.count(key)
        uuid_list = sorted(uuid_cnts.keys(), key=lambda x:uuid_cnts[x], reverse=True)
        if uuid_list:
            for u_key in uuid_list[0:self.depth]:
                res = self.backend.getkey(u_key)
                diff_cnt = len(set(_keys).symmetric_difference(set(res["keylist"])))
                if ceil((float(diff_cnt) / float(_ent_cnt)) * 100) < 100-self.match_required:
                    return res["result"]

    def __call__(self, *a):
        """Call wrapper that proxies the function call
        
        Args:
            *a: Argument list
        
        Returns:
            *: Result of executing the function
        """
        if self.is_enabled:
            res = self.lookup(a[0])
            if res:
                log.info("Cached result for %s" % a[0])
                return res
            else:
                res = self.func(*a)
                self.save(a[0], res)
                log.info("Added caching for %s" % a[0])
                return res
        else:
            return self.func(*a)


def setup_cache_fromsettings(settings):
    """Sets up the caching from the provided settings
    
    Args:
        settings (DICT): Pyramid Settings
    """
    GoogleGeocodeCache.is_enabled = asbool(settings.get("cache.enabled"))
    GoogleGeocodeCache.depth = int(settings.get("cache.depth", 6))
    GoogleGeocodeCache.match_required = int(settings.get("cache.match_required", 80))
    if backend_urn_re.search(settings.get("cache.backend", "dict")):
        if "://" in settings.get("cache.backend", ""):
            backend, cnf = settings.get("cache.backend").split("://")
        else:
            backend = settings.get("cache.backend", "dict")
            cnf = ""
        if backend in _backends:
            _resolved_backend = _backends[backend]
            GoogleGeocodeCache.backend = _resolved_backend(cnf)
    
def includeme(config):
    setup_cache_fromsettings(config.registry.settings)