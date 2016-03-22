#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.serial import *


class TestSerialLink():
    def __init__(self, bcPinRx, bcPinTx):
        self.SEND_INTERVAL_MS = 2000

        # Get a SerialLink
        self.serialLink = SerialLink()
        self.serialLink.Init(bcPinRx, bcPinTx, self.OnRx)

        # Set up timer to periodically send data
        evm_SetTimeout(self.OnTimeoutTx, self.SEND_INTERVAL_MS)

    def OnRx(self, hdr, byteList):
        print("OnRx")

        Log("HDR: %i bytes" % hdr.GetSize())
        Log("  Preamble  : %3i" % hdr.GetPreamble())
        Log("  DataLength: %3i" % hdr.GetDataLength())
        Log("  Checksum  : %3i" % hdr.GetChecksum())
        Log("  ProtocolId: %3i" % hdr.GetProtocolId())

        count = len(byteList)
        Log("MSG: %i bytes" % count)
        for byte in byteList:
            Log(("  %3i" % byte))

    def OnTimeoutTx(self):
        protocolId = 1
        self.serialLink.Send(protocolId, "heynow")
        evm_SetTimeout(self.OnTimeoutTx, self.SEND_INTERVAL_MS)


def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <bcPinRx> <bcPinTx>")
        sys.exit(-1)

    bcPinRx = int(sys.argv[1])
    bcPinTx = int(sys.argv[2])

    tsl = TestSerialLink(bcPinRx, bcPinTx)

    Log("Waiting")
    evm_MainLoop()


Main()


