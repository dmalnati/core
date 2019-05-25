#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from lib.utl import *
from lib.serial import *


class TestSerialLink():
    def __init__(self, bcPinRx, bcPinTx, verbose):
        self.SEND_INTERVAL_MS = 2000

        self.verbose = verbose

        # Get a SerialLink
        self.serialLink = SerialLink(bcPinRx, bcPinTx)

        self.serialLink.SetCbOnRxAvailable(self.OnRx)

    def OnRx(self, hdr, byteList):
        if self.verbose:
            Log("HDR: %i bytes" % hdr.GetSize())
            Log("  Preamble  : %3i" % hdr.GetPreamble())
            Log("  DataLength: %3i" % hdr.GetDataLength())
            Log("  Checksum  : %3i" % hdr.GetChecksum())
            Log("  ProtocolId: %3i" % hdr.GetProtocolId())

        count = len(byteList)
        if self.verbose:
            Log("MSG: %i bytes" % count)

        for byte in byteList:
            Log(("  %3i" % byte))

        if self.verbose:
            print("")


def Main():
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: " + sys.argv[0] + " <bcPinRx> <bcPinTx> [-v]")
        sys.exit(-1)

    bcPinRx = int(sys.argv[1])
    bcPinTx = int(sys.argv[2])
    verbose = 0

    if len(sys.argv) == 4:
        verbose = 1

    tsl = TestSerialLink(bcPinRx, bcPinTx, verbose)

    Log("Waiting")
    evm_MainLoop()


Main()


