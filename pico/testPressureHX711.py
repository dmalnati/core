#!/usr/bin/python

import time

from libHX711 import *


PIN_CLK    = 23
PIN_SERIAL = 24

sensor = HX711(PIN_CLK, PIN_SERIAL)

while True:
    print("val: %i" % (sensor.GetMeasurement()))
    time.sleep(1)

