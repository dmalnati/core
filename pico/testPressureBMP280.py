#!/usr/bin/python

import time

from libBMP280 import *


def Main():
    sensor = BMP280()

    while True:
        sensor.TakeMeasurement()
        print("%i" % (int(sensor.GetPressure())))

        time.sleep(1)

try:
    Main()
except KeyboardInterrupt:
    pass

