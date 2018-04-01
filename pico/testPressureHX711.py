#!/usr/bin/python

import time
import sys

from libHX711 import *


PIN_CLK    = 23
PIN_SERIAL = 24


def Main():
    sensor = HX711(PIN_CLK, PIN_SERIAL)

    # Check for optional gain setting
    if len(sys.argv) == 2:
        gain = int(sys.argv[1])
        sensor.SetGain(gain)

    print("date,time,val")
    while True:
        dateStr = time.strftime("%Y-%m-%d")
        timeStr = time.strftime("%H:%M:%S")
        val     = sensor.GetMeasurement()

        print("%s,%s,%i" % (dateStr, timeStr, val))
        sys.stdout.flush()

        time.sleep(1)

try:
    Main()
except KeyboardInterrupt:
    pass

