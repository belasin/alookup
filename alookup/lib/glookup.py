"""
Google Lookup System
"""

class InvalidAPRequest(Exception):
    pass

def lookup_cache(apscan):
    pass

def format_ap_entry(ap_entry):
    """Processes the Access Point dictionary and produce a stripped down entry for use in the request dataset
    
    Args:
        ap_entry (DICT): Access Point dict entry
    """
    return dict(
        macAddress = ap_entry["bssid"],
        signalStrength = int(ap_entry["rssi"]),
        age = 0,
        channel = int(ap_entry["channel"])
    )

def normalise_request(apscan):
    """Attempts to locate the access point information and return it as a list of access points
    
    Args:
        apscan (DICT|LIST): Description
    """

    out = []
    if type(apscan) == dict:
        #We need to itterate through the key values and
        # look for a list of dictionaries where a bssid key exists
        for k,v in apscan.items():
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

def perform_lookup(apscan):
    """Sends a request to google's geolocation service to lookup the location
    based on the Access Point list provided in the request
    
    Args:
        apscan (DICT|LIST): a list of access points
    """
    #We need to start by assuming we may not get the information
    #In the correct format
    apscan = normalise_request(apscan)

    if not apscan:
        raise InvalidAPRequest("Invalid Request")
	print(repr(apscan))
	pass