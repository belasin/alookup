"""
Google Lookup System
"""
import logging
import requests
import json
from caching import GoogleGeocodeCache as cache

log = logging.getLogger("google.geolocation")


class InvalidConfiguration(Exception):

    """Summary
    """

    pass


class InvalidAPRequest(Exception):

    """Summary
    """

    pass


def format_ap_entry(ap_entry):
    """Processes the Access Point dictionary and produce a stripped down entry for use in the request dataset

    Args:
        ap_entry (DICT): Access Point dict entry
    """
    return dict(
        macAddress=ap_entry["bssid"],
        signalStrength=int(ap_entry["rssi"]),
        age=0,
        channel=int(ap_entry["channel"])
    )


def normalise_request(apscan):
    """Attempts to locate the access point information and return it as a list of access points

    Args:
        apscan (DICT|LIST): Description
    """

    out = []
    if type(apscan) == dict:
        # We need to itterate through the key values and
        # look for a list of dictionaries where a bssid key exists
        for k, v in apscan.items():
            if type(v) == list:
                out = normalise_request(v)
                if out:
                    return out
    elif type(apscan) == list:
        for ent in apscan:
            formatted_ent = format_ap_entry(ent)
            if formatted_ent:
                out += [formatted_ent]
    return out


@cache
def geolocate(apscan, settings={}):
    """Summary

    Args:
        apscan (TYPE): Description
        settings (dict, optional): Description

    Returns:
        TYPE: Description

    Raises:
        InvalidConfiguration: Description
    """
    log.debug("Request for: %s" % apscan)
    api_key = settings.get("geolocate.api_key")
    if not api_key:
        raise InvalidConfiguration(
            "geolocate.api_key has not been set in the config")
    url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + api_key
    _post_info = dict(wifiAccessPoints=apscan)
    response = requests.post(url, data=json.dumps(_post_info))
    if response.status_code == 200:
        return response.json()


def perform_lookup(apscan, settings=None):
    """Sends a request to google's geolocation service to lookup the location
    based on the Access Point list provided in the request

    Args:
        apscan (DICT|LIST): a list of access points
    """
    # We need to start by assuming we may not get the information
    # In the correct format
    if not settings:
        settings = get_current_registry().settings
    apscan = normalise_request(apscan)
    if not apscan:
        raise InvalidAPRequest("Invalid Request")
    return geolocate(apscan, settings)
