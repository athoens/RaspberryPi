# -*- coding: utf-8 -*-

import os

sensorPath = "testdata"
slaves = ["localhost:8090"]
masterPort = 8080
slavePort = 8090
openWeatherMapApiKey = os.environ.get('OPEN_WEATHER_MAP_API_KEY')
openWeatherMapLat = os.environ.get('OPEN_WEATHER_MAP_LAT')
openWeatherMapLong = os.environ.get('OPEN_WEATHER_MAP_LONG')
collectInterval = 10
maxHistoryLength = 50
