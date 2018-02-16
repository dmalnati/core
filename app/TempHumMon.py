#!/usr/bin/python

import sys
import os
import time                                
import smbus


SI7021_DEVICE_ID = 0x40


def GetHumidity():
    bus = smbus.SMBus(1)

    bus.write_byte(SI7021_DEVICE_ID, 0xF5) 

    time.sleep(0.1)

    data0 = bus.read_byte(SI7021_DEVICE_ID)
    data1 = bus.read_byte(SI7021_DEVICE_ID)

    humidity = int(((data0 * 256 + data1) * 125 / 65536.0) - 6)

    return humidity
		
	
def GetTemperatureF():
    bus = smbus.SMBus(1)

    bus.write_byte(SI7021_DEVICE_ID, 0xF3)

    time.sleep(0.3)

    data0 = bus.read_byte(SI7021_DEVICE_ID)
    data1 = bus.read_byte(SI7021_DEVICE_ID)

    tempC = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
    tempF = int(tempC * 1.8 + 32)

    return tempF


def UpdateDweet(tempF, hum):
    DWEET_ID = "fid-jc-desk-059"

    cmd  = "wget -q -O /dev/null "
    cmd += "\"https://dweet.io/dweet/for/%s?" % (DWEET_ID)
    cmd += "temp=%s&hum=%s\"" % (tempF, hum)

    #print cmd
    os.system(cmd)


def UpdateThingsboard(tempF, hum):
    ACCESS_TOKEN = "KUZ7dEq9JrvFfNHSKVe4"

    cmd  = "curl -X POST -d "
    cmd += '"{\\"temperature\\":%s, \\"humidity\\":%s}" ' % (tempF, hum)
    cmd += "http://demo.thingsboard.io/api/v1/%s/telemetry " % ACCESS_TOKEN
    cmd += '--header "Content-Type:application/json"'

    #print cmd
    os.system(cmd)


def Main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <reportIntervalSecs>")
        sys.exit(-1)

    reportIntervalSecs = float(sys.argv[1])

    while True:
        try:
            tempF = GetTemperatureF()
            hum   = GetHumidity()

            print "temp: %s, hum: %s" % (tempF, hum)

            UpdateThingsboard(tempF, hum)
        except:
            pass

        time.sleep(reportIntervalSecs)



Main()





