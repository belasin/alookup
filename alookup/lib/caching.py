from functools import update_wrapper
from pyramid.threadlocal import get_current_registry
from pyramid.settings import asbool
import re

class DictBackend(object):
    def __init__(self, cnf):
        self.data = {}

class RedisBackend(object):
    def __init__(self, cnf):
        raise NotImplemented("Place Holder for Later")

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
        k = [i for i in signal_bands.keys() if i >= ent["signalStrength"]][0]
        sband = signal_bands[k]
        return "%s::%s" % (ent["macAddress"], sband)

    def lookup_cache(self, apscan):
        apscan = sorted(apscan, key=lambda x:x["signalStrength"],reverse=True)
        print self.backend
        pass

    def __call__(self, *a):
        if self.is_enabled:
            res = self.lookup_cache(apscan)
            if res:
                return res
        res = self.func(*a)
        return res


def setup_cache_fromsettings(settings):
    """Sets up the caching from the provided settings
    
    Args:
        settings (DICT): Pyramid Settings
    """
    GoogleGeocodeCache.is_enabled = asbool(settings.get("cache.enable"))
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