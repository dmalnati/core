#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.serial import *



def Main():
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: "   +
              sys.argv[0] +
              " <bcPinRx> [<bcPinTx=->] [<baud=9600>]")
        print("    bcPinRx can be - if not in use (write only)")
        print("    bcPinTx can be - if not in use (read only)")
        sys.exit(-1)

    # set default arguments
    bcPinRx = sys.argv[1]
    bcPinTx = "-"
    baud    = 9600

    if len(sys.argv) > 2:
        bcPinTx = sys.argv[2]

        if len(sys.argv) > 3:
            baud = sys.argv[3]

    # parse arguments
    bcPinRx = None if bcPinRx == "-" else int(bcPinRx)
    bcPinTx = None if bcPinTx == "-" else int(bcPinTx)
    baud    = int(baud)

    # create serial comms object
    ser = SerialRaw(bcPinRx, bcPinTx, baud)

    # create callbacks
    def OnSerialReadable(byteList):
        sys.stdout.write(byteList)
        sys.stdout.flush()

    def OnKeyboardReadable(byteList):
        ser.Send(byteList)

    # register callbacks
    ser.SetCbOnRxAvailable(OnSerialReadable)
    WatchStdinEndLoopOnEOF(OnKeyboardReadable, binary=True)

    evm_MainLoop()

    ser.Stop()


Main()


