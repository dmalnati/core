#!/usr/bin/python

import sys
import time

from libBMP280 import *


def Main():
    sensor = BMP280()

    print("date,time,hPa")
    while True:
        sensor.TakeMeasurement()

        dateStr     = time.strftime("%Y-%m-%d")
        timeStr     = time.strftime("%H:%M:%S")
        pressureHPa = sensor.GetPressureHPa()

        print("%s,%s,%i" % (dateStr, timeStr, pressureHPa))
        sys.stdout.flush()

        time.sleep(1)

try:
    Main()
except KeyboardInterrupt:
    pass

