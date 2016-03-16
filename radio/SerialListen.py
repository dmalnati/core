#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


pigd = None

def SerialListen(bcPin):
    global pigd

    baud = 9600
    msDelay = 0

    # open pin for reading serial
    pigd.bb_serial_read_open(bcPin, baud)

    # set up timer to check on incoming data
    def OnTimeout():
        (count, byteList) = pigd.bb_serial_read(bcPin)

        if count:
            #print("Got " + str(count) + " bytes:")

            for byte in byteList:
                v = float(byte) / 255. * 5.0

                Log(("%3i" % byte) + " -> " + ("%.2f" % v))

        evm_SetTimeout(OnTimeout, msDelay)

    evm_SetTimeout(OnTimeout, msDelay)



def Main():
    global pigd

    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <bcPin>")
        sys.exit(-1)

    bcPin = int(sys.argv[1])

    pigd = pigpio.pi()
    SerialListen(bcPin)

    Log("Waiting")
    evm_MainLoop()

    pigd.bb_serial_read_close(bcPin)
    pigd.stop()


Main()


