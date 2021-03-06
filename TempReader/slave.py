#!/usr/bin/env python3
import logging
import connexion
import pathlib
import os
import threading

if os.environ.get('ENVIRONMENT', 'DEV') == 'PROD':
    from config import prod as config  # config/prod.py
else:
    from config import dev as config  # config/dev.py

sensor_lock = threading.Lock()


def read_temperature(sensor_id):
    logging.debug("Reading sensor %s", sensor_id)
    # Open the file that we viewed earlier so that python can see what is in it. Replace the serial number as before.
    tfile = open("{0}/{1}/w1_slave".format(config.sensorPath, sensor_id))
    # Read all of the text in the file.
    text = tfile.read()
    # Close the file now that the text has been read.
    tfile.close()

    # Split the text with new lines (\n) and select the second line.
    firstline = text.split("\n")[0]
    # Split the line into words, referring to the spaces, and select the 10th word (counting from 0).
    crcOk = firstline.split(" ")[11]
    if crcOk != "YES":
        return None

    # Split the text with new lines (\n) and select the second line.
    secondline = text.split("\n")[1]
    # Split the line into words, referring to the spaces, and select the 10th word (counting from 0).
    temperaturedata = secondline.split(" ")[9]
    # The first two characters are "t=", so get rid of those and convert the temperature from a string to a number.
    temperature = float(temperaturedata[2:])
    # Put the decimal point in the right place and display it.
    return temperature / 1000


def get_sensors():
    with sensor_lock:
        sensor_ids = os.listdir(config.sensorPath)
        result = {}
        for sensor_id in sensor_ids:
            if os.path.isfile("{0}/{1}/w1_slave".format(config.sensorPath, sensor_id)):
                temperature = read_temperature(sensor_id)
                if temperature and temperature>-20 and temperature<90:
                    result[sensor_id] = {"temperature": temperature}
        return result


def get_sensor(sensor_id):
    return {
        sensor_id: {
            "temperature": read_temperature(sensor_id)
        }
    }
#    return pet or ('Not found', 404)


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename="slave.log", filemode='w', level=logging.DEBUG, format=FORMAT)
app = connexion.App(__name__)
app.add_api(pathlib.Path('swagger-slave.yaml'))
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=config.slavePort, server='tornado')
