#!/usr/bin/python

from libBMP280 import *

sensor = BMP280()

sensor.TakeMeasurement()
print("TempF   : %s" % (sensor.GetTempF()))
print("Pressure: %s" % (sensor.GetPressure()))


