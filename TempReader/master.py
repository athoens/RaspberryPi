#!/usr/bin/env python3
import logging
import connexion
import json
import urllib.request
import urllib.error
import pathlib
import os

outsideTemperatureUrl = "http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&APPID={apiKey}"

if os.environ.get('ENVIRONMENT', 'DEV') == 'PROD':
    from config import prod as config  # config/prod.py
else:
    from config import dev as config  # config/dev.py


def read_slave(host):
    response = urllib.request.urlopen('http://{0}/sensors'.format(host))
    response_text = response.read().decode()
    return json.loads(response_text)


def readOutsideTemp():
    try:
        response = urllib.request.urlopen(outsideTemperatureUrl.format(lat=config.openWeatherMapLat, lon=config.openWeatherMapLong, apiKey=config.openWeatherMapApiKey))
        response_text = response.read().decode()
        return float(json.loads(response_text)["main"]["temp"])
    except Exception:
        return "?"


def get_sensors():
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
            "temperature": readOutsideTemp()
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

    return results


def get_sensor():
    return 'Not found', 404


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api(pathlib.Path('swagger-master.yaml'))
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=config.masterPort, server='gevent')