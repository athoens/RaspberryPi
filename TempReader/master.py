#!/usr/bin/env python3
import logging
import connexion
import json
import urllib2
import os

if os.environ.get('ENVIRONMENT', 'DEV') == 'PROD':
    from config import prod as config  # config/prod.py
else:
    from config import dev as config  # config/dev.py


def read_slave(host):
    data = json.load(urllib2.urlopen('http://{0}/sensors'.format(host)))
    return data


def get_sensors():
    result = []
    for slave in config.slaves:
        result += read_slave(slave)
    for sensor in result:
        if sensor["id"] in config.sensor_info:
            sensor["name"] = config.sensor_info[sensor["id"]]["name"]
    return result


def get_sensor():
    return 'Not found', 404


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api('swagger-master.yaml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=config.masterPort, server='gevent')
