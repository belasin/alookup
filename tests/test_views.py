"""Summary

Attributes:
    api_key (str): Description
    test_json_body (TYPE): Description
"""
from alookup.views.default import lookup_view
from alookup.lib.caching import setup_cache_fromsettings
from alookup.lib.caching import GoogleGeocodeCache
from pyramid.testing import DummyRequest
import pytest

test_json_body = {
    "apscan_data": [
      {
        "band": "2.4",
        "bssid": "9c:b2:b2:66:c1:be",
        "channel": "5",
        "frequency": 2432,
        "rates": "1.0 - 135.0 Mbps",
        "rssi": -35,
        "security": "wpa-psk",
        "ssid": "HUAWEI-B315-C1BE",
        "timestamp": 1522886457.0,
        "vendor": "HUAWEI TECHNOLOGIES CO.,LTD",
        "width": "20"
      },
      {
        "band": "2.4",
        "bssid": "84:78:ac:b9:76:19",
        "channel": "1",
        "frequency": 2412,
        "rates": "6.5 - 270.0 Mbps",
        "rssi": -56,
        "security": "wpa-eap",
        "ssid": "1 Telkom Connect",
        "timestamp": 1522886457.0,
        "vendor": "Cisco Systems, Inc",
        "width": "20"
      },
      {
        "band": "2.4",
        "bssid": "c0:a0:bb:c4:10:d6",
        "channel": "1",
        "frequency": 2412,
        "rates": "1.0 - 54.0 Mbps",
        "rssi": -66,
        "security": "wpa-psk",
        "ssid": "default",
        "timestamp": 1522886457.0,
        "vendor": "D-Link International",
        "width": "40"
      },
      {
        "band": "5.0",
        "bssid": "84:78:ac:b9:76:16",
        "channel": "56",
        "frequency": 5280,
        "rates": "6.5 - 270.0 Mbps",
        "rssi": -82,
        "security": "wpa-eap",
        "ssid": "1 Telkom Connect",
        "timestamp": 1522886457.0,
        "vendor": "Cisco Systems, Inc",
        "width": "20"
      },
      {
        "band": "5.0",
        "bssid": "e8:1d:a8:28:a6:6c",
        "channel": "36",
        "frequency": 5180,
        "rates": "6.0 - 866.7 Mbps",
        "rssi": -65,
        "security": "open",
        "ssid": "@VAST",
        "timestamp": 1522886457.0,
        "vendor": "Ruckus Wireless",
        "width": "80"
      },
      {
        "band": "2.4",
        "bssid": "e8:1d:a8:28:a6:68",
        "channel": "8",
        "frequency": 2447,
        "rates": "6.0 - 135.0 Mbps",
        "rssi": -52,
        "security": "open",
        "ssid": "@VAST",
        "timestamp": 1522886457.0,
        "vendor": "Ruckus Wireless",
        "width": "20"
      },
      {
        "band": "2.4",
        "bssid": "e8:1d:a8:68:a6:68",
        "channel": "8",
        "frequency": 2447,
        "rates": "6.0 - 135.0 Mbps",
        "rssi": -53,
        "security": "open",
        "ssid": "McDonalds@VAST",
        "timestamp": 1522886457.0,
        "vendor": "Ruckus Wireless",
        "width": "20"
      },
      {
        "band": "2.4",
        "bssid": "84:78:ac:b9:76:1a",
        "channel": "1",
        "frequency": 2412,
        "rates": "6.5 - 270.0 Mbps",
        "rssi": -57,
        "security": "open",
        "ssid": "1 Telkom Guest",
        "timestamp": 1522886457.0,
        "vendor": "Cisco Systems, Inc",
        "width": "20"
      },
      {
        "band": "5.0",
        "bssid": "84:78:ac:b9:76:15",
        "channel": "56",
        "frequency": 5280,
        "rates": "6.5 - 270.0 Mbps",
        "rssi": -82,
        "security": "open",
        "ssid": "1 Telkom Guest",
        "timestamp": 1522886457.0,
        "vendor": "Cisco Systems, Inc",
        "width": "20"
      },
      {
        "band": "5.0",
        "bssid": "e8:1d:a8:68:a6:6c",
        "channel": "36",
        "frequency": 5180,
        "rates": "6.0 - 866.7 Mbps",
        "rssi": -66,
        "security": "open",
        "ssid": "McDonalds@VAST",
        "timestamp": 1522886457.0,
        "vendor": "Ruckus Wireless",
        "width": "80"
      }
    ]
}

api_key = "AIzaSyCCK6hPzvUI1_XbDCV4pC1HN_6bneUejYc"

@pytest.fixture
def apscan_data(app):
    """Summary
    
    Args:
        app (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    app.registry.settings["geolocate.api_key"] = api_key
    app.registry.settings["cache.enabled"] = "True"
    setup_cache_fromsettings(app.registry.settings)
    request = DummyRequest(json_body=test_json_body, method="POST")
    request.registry = app.registry
    request.host = 'example.com'
    data = test_json_body.copy()
    del data["apscan_data"][5]
    request_partial = DummyRequest(json_body=data, method="POST")
    request_partial.registry = app.registry
    request_partial.host = 'example.com'
    return request, request_partial

def test_perform_lookup(apscan_data):
    """Summary
    
    Args:
        apscan_data (TYPE): Description
    """
    data_full, data_partial = apscan_data
    res = lookup_view(data_full)
    assert data_full.response.status_int == 200
    assert res != None
    assert len(GoogleGeocodeCache.backend.data.keys()) > 0
    assert res["location"] != None
    res = lookup_view(data_partial)
    assert data_partial.response.status_int == 200
    assert res != None
    assert len(GoogleGeocodeCache.backend.data.keys()) > 0
    assert res["location"] != None
