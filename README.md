ALOOKUP
=======

Simple application that takes a scan of access points in an area, it will then send that list through to google's geolocation service which will then attempt to determine the approximate gps co-ordindates.

Additionally a rudementary caching system has been incorporated that will attempt to cache the results and match furture calls in an effort to reduce the number of requests that are sent to google.

Installation
============

## Manual Method

I suggest that you use virtualenv to setup an isolated python environment to execute and work with this application

```
	git clone https://github.com/jpunwin/alookup.git alookup
	virtualenv alookup
	source alookup/bin/activate
	pip install alookup
	pserve production.ini
```

## Docker

```
	docker build -t junwin/alookup https://github.com/jpunwin/alookup.git
	docker run -p 8080:8080 junwin/alookup:latest
```

Testing
=======

You can simply use cURL if you want to perform a post request

```
curl --request POST --data '{
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
}' http://localhost:8080
```

TODO
====

Some things that need to be done
 - Need to add in the RedisBackend for the caching system
 - Add kubernetes documentation
 - Could theoretically be easily converted to Python3
 - Add some direct testing of the caching system
 - Cache entries need a TTL, the DictBackend will need to invalidate cached items after a configured amount of time