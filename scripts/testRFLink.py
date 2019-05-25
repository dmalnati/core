#!/usr/bin/python

import sys
import os
import time

import pigpio

from libCore import *
from libRFLink import *


class TestRFLink():
    def __init__(self, rfLink):
        self.rfLink = rfLink

        # Set default addressing and protocol
        self.SetRealm(1)
        self.SetSrcAddr(0)
        self.SetDstAddr(1)
        self.SetProtocolId(1)

        self.rfLink.SetCbOnRxAvailable(self.OnRx)

        WatchStdinEndLoopOnEOF(self.OnStdin)

    def SetRealm(self, realm):
        self.realm = int(realm)

    def SetSrcAddr(self, srcAddr):
        self.srcAddr = int(srcAddr)

    def SetDstAddr(self, dstAddr):
        self.dstAddr = int(dstAddr)

    def SetProtocolId(self, protocolId):
        self.protocolId = int(protocolId)

    def PrintHdrAndData(self, hdr, byteList):
        Log("HDR:")
        Log("  Realm     : %3i" % hdr.GetRealm())
        Log("  SrcAddr   : %3i" % hdr.GetSrcAddr())
        Log("  DstAddr   : %3i" % hdr.GetDstAddr())
        Log("  ProtocolId: %3i" % hdr.GetProtocolId())
        Log("Data:")
        for byte in byteList:
            Log("  %3i" % byte)
        Log("")

    def OnRx(self, hdr, byteList):
        Log("Received RFLink Data")

        self.PrintHdrAndData(hdr, byteList)
    
    def OnStdin(self, line):
        byteList = bytearray(line)

        if line[0:2] == "0x":
            byteList = bytearray.fromhex(line[2:])

        Log("Stdin bytes:")
        for byte in byteList:
            Log("  %3i" % byte)

        # Construct RFLink Header
        hdr = RFLinkHeader()

        hdr.SetRealm(self.realm)
        hdr.SetSrcAddr(self.srcAddr)
        hdr.SetDstAddr(self.dstAddr)
        hdr.SetProtocolId(self.protocolId)

        # Send header and bytes from stdin
        Log("Sending")

        self.PrintHdrAndData(hdr, byteList)

        self.rfLink.Send(hdr, byteList)


def Main():
    if len(sys.argv) != 7:
        print("Usage: " +
              sys.argv[0] +
              " <bcPinRx> <bcPinTx> <realm> <srcAddr> <dstAddr> <protocolId>")
        sys.exit(-1)

    bcPinRx    = int(sys.argv[1])
    bcPinTx    = int(sys.argv[2])
    realm      = int(sys.argv[3])
    srcAddr    = int(sys.argv[4])
    dstAddr    = int(sys.argv[5])
    protocolId = int(sys.argv[6])

    # Get SerialLink, and RFLink to sit on top of it
    serialLink = SerialLink(bcPinRx, bcPinTx)
    rfLink     = RFLinkOverSerial(serialLink)

    # Create and configure RFLink-using class
    test = TestRFLink(rfLink) 
    test.SetRealm(realm)
    test.SetSrcAddr(srcAddr)
    test.SetDstAddr(dstAddr)
    test.SetProtocolId(protocolId)

    Log("Waiting")
    evm_MainLoop()


Main()


