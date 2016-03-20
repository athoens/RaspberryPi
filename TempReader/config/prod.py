# -*- coding: utf-8 -*-

import os

sensorPath = "/sys/bus/w1/devices"
slaves = ["192.168.2.210:8090", "192.168.2.211:8090"]
masterPort = 80
slavePort = 8090
openWeatherMapApiKey = os.environ.get('OPEN_WEATHER_MAP_API_KEY')
openWeatherMapLat = os.environ.get('OPEN_WEATHER_MAP_LAT')
openWeatherMapLong = os.environ.get('OPEN_WEATHER_MAP_LONG')
collectInterval = 60
maxHistoryLength = 6000
