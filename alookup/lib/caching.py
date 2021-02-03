from functools import update_wrapper
from pyramid.threadlocal import get_current_registry
from pyramid.settings import asbool
import uuid
import re

class DictBackend(object):
    def __init__(self, cnf):
        self.data = {}

    def flush(self):
        self.data = {}

    def addkey(self, key, value):
        raise NotImplemented

    def appendkey(self, key, value):
        raise NotImplemented

    def getkey(key):
        raise NotImplemented

    def getkey(key):
        raise NotImplemented

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
        30: "A",
        40: "B",
        60: "C",
        80: "D",
        9999: "E"
    }

    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def generate_cache_key(self, ent):
        k = [i for i in self.signal_bands.keys() if i >= ent["signalStrength"]][0]
        sband = self.signal_bands[k]
        return "%s::%s" % (ent["macAddress"], sband)

    def save(self, apscan, result):
        apscan = sorted(apscan, key=lambda x:x["signalStrength"],reverse=True)
        _id = uuid.uuid4()
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
        self.backend.addkey(_id, _data)

    def lookup(self, apscan):
        apscan = sorted(apscan, key=lambda x:x["signalStrength"],reverse=True)
        for ent in apscan:
            k = self.generate_cache_key(ent)
            print k
        print self.backend

    def __call__(self, *a):
        print self.is_enabled
        if self.is_enabled:
            res = self.lookup(a[0])
            if res:
                return res
            else:
                res = self.func(*a)
                self.save(a[0], res)
            raise Exception("GOTHERE")
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
    coerce_config(config.registry.settings)