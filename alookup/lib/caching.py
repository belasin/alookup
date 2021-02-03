from functools import update_wrapper
from pyramid.threadlocal import get_current_registry
from pyramid.settings import asbool
from math import ceil
import uuid
import re
import logging

log = logging.getLogger("alookup.caching")


class DictBackend(object):
    def __init__(self, cnf):
        log.info("Caching started with DictBackend")
        self.data = {}

    def flush(self):
        self.data = {}

    def setkey(self, key, value):
        self.data[key] = value

    def appendkey(self, key, value):
        if key in self.data:
            if type(self.data[key]) != list:
                raise TypeError("Data type is not a list")
            else:
                self.data[key].append(value)
        else:
            self.data[key] = [value]

    def getkey(self, key):
        return self.data.get(key)

    def iskey(self, key):
        return key in self.data

class RedisBackend(object):
    def __init__(self, cnf):
        raise NotImplemented("Definately can be done if you wanted to scale the system")

backend_urn_re = re.compile("^(dict|redis\:\/\/(.*){3,5})$")

_backends = {
    "dict": DictBackend,
    "redis": RedisBackend
}

class GoogleGeocodeCache(object):
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
        update_wrapper(self, func)
        self.func = func

    def generate_cache_key(self, ent):
        k = [i for i in sorted(self.signal_bands.keys()) if i >= -ent["signalStrength"]][0]
        sband = self.signal_bands[k]
        return "%s::%s" % (ent["macAddress"], sband)

    def save(self, apscan, result):
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
        print self.is_enabled
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