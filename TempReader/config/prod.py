# -*- coding: utf-8 -*-

import os

sensorPath = "/sys/bus/w1/devices"
slaves = ["192.168.2.210:8090", "192.168.2.211:8090"]
sensor_info = {
    "28-0000067a9b24": {
        "name": "Raumtemperatur Wohnzimmer"
    },
    "28-0415a4658dff": {
        "name": "Zufluss Wohnzimmer"
    },
    "28-0415a40bafff": {
        "name": "Abfluss Wohnzimmer"
    },
    "28-0415a40a21ff": {
        "name": "Zufluss Kinderzimmer"
    }
    ,
    "28-0315a47057ff": {
        "name": "Heizkörper Kinderzimmer"
    },
    "28-0415a463d4ff": {
        "name": "Raumtemperatur Kinderzimmer"
    },
    "outside": {
        "name": "Außentemperatur"
    }
}
masterPort = 80
slavePort = 8090
openWeatherMapApiKey = os.environ.get('OPEN_WEATHER_MAP_API_KEY')
openWeatherMapLat = os.environ.get('OPEN_WEATHER_MAP_LAT')
openWeatherMapLong = os.environ.get('OPEN_WEATHER_MAP_LONG')
