#!/usr/bin/python

import time
import sys

from libHX711 import *


PIN_CLK    = 23
PIN_SERIAL = 24


def Main():
    if len(sys.argv) != 6:
        print("Usage: %s <reportSecs> <gain> <subtract> <divide> <label>" % (sys.argv[0]))
        sys.exit(-1)

    reportSecs = int(sys.argv[1])
    gain       = int(sys.argv[2])
    subtract   = float(sys.argv[3])
    divide     = float(sys.argv[4])
    label      = sys.argv[5]

    sensor = HX711(PIN_CLK, PIN_SERIAL)

    sensor.SetGain(gain)
    sensor.SetCalibration(subtract, divide)

    print("date,time,%s" % (label))
    while True:
        dateStr = time.strftime("%Y-%m-%d")
        timeStr = time.strftime("%H:%M:%S")
        val     = sensor.GetMeasurement()

        print("%s,%s,%i" % (dateStr, timeStr, val))
        sys.stdout.flush()

        time.sleep(reportSecs)

try:
    Main()
except KeyboardInterrupt:
    pass

