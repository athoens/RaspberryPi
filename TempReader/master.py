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
import copy
import time

import connexion
import collections

outsideTemperatureUrl = "http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&APPID={apiKey}"
headers = {"Access-Control-Allow-Origin": "*"}
data = collections.OrderedDict()
history_lock = threading.Lock()


if os.environ.get('ENVIRONMENT', 'DEV') == 'PROD':
    from config import prod as config  # config/prod.py
else:
    from config import dev as config  # config/dev.py


def read_slave(host):
    response = urllib.request.urlopen('http://{0}/sensors'.format(host), timeout=30)
    response_text = response.read().decode()
    return json.loads(response_text)


def read_outside_temp():
    try:
        response = urllib.request.urlopen(outsideTemperatureUrl.format(lat=config.openWeatherMapLat, lon=config.openWeatherMapLong,
                                                                       apiKey=config.openWeatherMapApiKey), timeout=30)
        response_text = response.read().decode()
        return float(json.loads(response_text)["main"]["temp"])
    except Exception:
        return "?"


def do_reading():
    logging.debug("Sensor reading started")
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
    logging.debug("Sensor reading completed")
    return readings


def get_sensors():
    logging.debug("Sensors request starting")
    results = do_reading()
    logging.debug("Sensors request completed")
    return results, 200, headers


def get_sensor_history():
    with history_lock:
        data_copy = copy.deepcopy(data)
    return data_copy, 200, headers


def get_collect():
    logging.info("Collect request starting")
    global data
    reading = do_reading()
    now = datetime.datetime.utcnow()
    current_time = int(calendar.timegm(now.utctimetuple()) + now.microsecond * 1e-6) * 1000
    with history_lock:
        for sensor_id, new_data in reading.items():
            sensor_data = data.get(sensor_id, [])
            sensor_data.append([current_time, new_data["temperature"]])
            while len(sensor_data) > config.maxHistoryLength:
                sensor_data.pop(0)
            data[sensor_id] = sensor_data
    logging.info("Collect request completed")
    return {}


def collect_thread():
    while True:
        try:
            logging.debug("Collect thread starting")
            urllib.request.urlopen('http://127.0.0.1:{}/collect'.format(config.masterPort), 60)
            logging.debug("Collect thread finished")
        except Exception:
            logging.error("Error in collect thread", exc_info=True)
        time.sleep(config.collectInterval)


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename="master.log", filemode='w', level=logging.DEBUG, format=FORMAT)

app = connexion.App(__name__)
app.add_api(pathlib.Path('swagger-master.yaml'))
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    t = threading.Thread(target=collect_thread, daemon=True)
    t.start()
    app.run(port=config.masterPort, server='tornado')

