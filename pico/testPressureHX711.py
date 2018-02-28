#!/usr/bin/python

import time
import sys

from libHX711 import *


PIN_CLK    = 23
PIN_SERIAL = 24


def Main():
    sensor = HX711(PIN_CLK, PIN_SERIAL)

    while True:
        print("%i" % (sensor.GetMeasurement()))
        sys.stdout.flush()
        time.sleep(1)

try:
    Main()
except KeyboardInterrupt:
    pass

