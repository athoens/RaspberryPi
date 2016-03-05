#!/usr/bin/env python3
import logging
import json
import urllib.request
import urllib.error
import pathlib
import os
import threading
import datetime
import calendar

import connexion
import collections

outsideTemperatureUrl = "http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&APPID={apiKey}"
headers = {"Access-Control-Allow-Origin": "*"}
data = collections.OrderedDict()

if os.environ.get('ENVIRONMENT', 'DEV') == 'PROD':
    from config import prod as config  # config/prod.py
else:
    from config import dev as config  # config/dev.py


def read_slave(host):
    response = urllib.request.urlopen('http://{0}/sensors'.format(host))
    response_text = response.read().decode()
    return json.loads(response_text)


def read_outside_temp():
    try:
        response = urllib.request.urlopen(outsideTemperatureUrl.format(lat=config.openWeatherMapLat, lon=config.openWeatherMapLong, apiKey=config.openWeatherMapApiKey))
        response_text = response.read().decode()
        return float(json.loads(response_text)["main"]["temp"])
    except Exception:
        return "?"


def do_reading():
    readings = {}
    # Read sensor of all slaves
    for slave in config.slaves:
        try:
            readings.update(read_slave(slave))
        except urllib.error.URLError:
            logging.warning("Could not read slave <%s>", slave, exc_info=True)

    # Read outside temperature
    if config.openWeatherMapApiKey is not None:
        readings["outside"] = {
            "temperature": read_outside_temp()
        }

    # Add names to sensor if present
    results = {}
    for sensor_id, sensor_metadata in config.sensor_info.items():
        result = sensor_metadata.copy()
        if sensor_id in readings:
            result.update(readings[sensor_id])
        else:
            result["temperature"] = "?"
        results[sensor_id] = result
    return readings


def get_sensors():
    results = do_reading()
    return results, 200, headers


def get_sensor_history():
    return data, 200, headers


def get_collect():
    do_collect()
    return {}


def get_sensor():
    return 'Not found', 404


def do_collect():
    global data
    reading = do_reading()
    now = datetime.datetime.utcnow()
    current_time = int(calendar.timegm(now.utctimetuple()) + now.microsecond * 1e-6) * 1000
    for sensor_id, new_data in reading.items():
        sensor_data = data.get(sensor_id, [])
        sensor_data.append([current_time, new_data["temperature"]])
        while len(sensor_data) > config.maxHistoryLength:
            sensor_data.pop(0)
        data[sensor_id] = sensor_data


def collect_timer():
    try:
        urllib.request.urlopen('http://127.0.0.1:{}/collect'.format(config.masterPort))
    finally:
        t2 = threading.Timer(config.collectInterval, collect_timer)
        t2.start()


logging.basicConfig(level=logging.INFO)

do_collect()
app = connexion.App(__name__)
app.add_api(pathlib.Path('swagger-master.yaml'))
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    t = threading.Timer(config.collectInterval, collect_timer)
    t.start()
    app.run(port=config.masterPort, server='gevent')

