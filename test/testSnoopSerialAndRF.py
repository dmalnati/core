#!/usr/bin/python3.5 -u

import sys
import os
import time

import pigpio

from libCore import *
from libSerialLink import *
from libRFLink import *
from libSimpleIPC import *



class Snoop():
    def __init__(self, bcPinSnoopRx, bcPinSnoopTx):
        # Create SerialLink to watch for inbound and outbound data
        serialLinkRx = SerialLink(bcPinSnoopRx, None)
        serialLinkTx = SerialLink(bcPinSnoopTx, None)

        # Set callbacks when data is received or being sent
        serialLinkRx.SetCbOnRxAvailable(self.OnSerialInboundData)
        serialLinkTx.SetCbOnRxAvailable(self.OnSerialOutboundData)

        # Create RFLink instance for parsing of data, not actual use
        self.rfLink = RFLinkOverSerial(None)

        # Create SimpleIPCProtocolHandler for parsing of data, not actual use
        self.ph = SimpleIPCProtocolHandler()


    #############################
    #
    # Serial Decode
    #
    #############################

    def OnSerialInboundData(self, hdrSerial, byteListSerial):
        print("Serial Inbound")
        hdrSerial.Print()

        if not self.AttemptRFLinkDecode(hdrSerial, \
                                        byteListSerial, \
                                        self.OnRFLinkInboundData):
            self.AttemptSimpleIPCDecode(hdrSerial, \
                                        byteListSerial, \
                                        self.OnSimpleIPCInboundData)

    def OnSerialOutboundData(self, hdrSerial, byteListSerial):
        print("Serial Outbound")
        hdrSerial.Print()

        if not self.AttemptRFLinkDecode(hdrSerial, \
                                        byteListSerial, \
                                        self.OnRFLinkOutboundData):
            self.AttemptSimpleIPCDecode(hdrSerial, \
                                        byteListSerial, \
                                        self.OnSimpleIPCOutboundData)


    #############################
    #
    # RFLink Decode
    #
    #############################


    def AttemptRFLinkDecode(self, hdrSerial, byteListSerial, cbFn):
        retVal = False

        rfHdrAndRfByteList = \
            self.rfLink.ParseRFLinkData(hdrSerial, byteListSerial)

        if rfHdrAndRfByteList:
            retVal = True
            (rfHdr, rfByteList) = rfHdrAndRfByteList

            cbFn(rfHdr, rfByteList)

        return retVal

    def OnRFLinkInboundData(self, hdrRFLink, byteListRFLink):
        print("RFLink Inbound")
        hdrRFLink.Print()

        self.AttemptSimpleIPCDecode(hdrRFLink, \
                                    byteListRFLink, \
                                    self.OnSimpleIPCInboundData)

    def OnRFLinkOutboundData(self, hdrRFLink, byteListRFLink):
        print("RFLink Outbound")
        hdrRFLink.Print()

        self.AttemptSimpleIPCDecode(hdrRFLink, \
                                    byteListRFLink, \
                                    self.OnSimpleIPCOutboundData)


    #############################
    #
    # SimpleIPC Decode
    #
    #############################


    def AttemptSimpleIPCDecode(self, hdr, byteList, cbFn):
        retVal = False

        hdrAndMsg = self.ph.ParseSimpleIPCData(hdr, byteList)

        if hdrAndMsg:
            retVal = True
            (hdr, msg) = hdrAndMsg

            cbFn(hdr, msg)

        return retVal

    def OnSimpleIPCInboundData(self, hdr, msg):
        print("SimpleIPC Inbound")
        hdr.Print()

        self.AttemptSimpleIPCMessageParse(msg, \
                                          self.OnSimpleIPCMessageInbound)

    def OnSimpleIPCOutboundData(self, hdr, msg):
        print("SimpleIPC Outbound")
        hdr.Print()

        self.AttemptSimpleIPCMessageParse(msg, \
                                          self.OnSimpleIPCMessageOutbound)


    #############################
    #
    # SimpleIPCMessage Decode
    #
    #############################

    def AttemptSimpleIPCMessageParse(self, msg, cbFn):
        retVal = False

        msgParsed = self.ph.ParseSimpleIPCMessage(msg)

        if msgParsed:
            retVal = True
            cbFn(msgParsed)

        return retVal

    def OnSimpleIPCMessageInbound(self, msgParsed):
        print("SimpleIPCMessage Inbound")
        msgParsed.Print()

    def OnSimpleIPCMessageOutbound(self, msgParsed):
        print("SimpleIPCMessage Outbound")
        msgParsed.Print()



###################################################################

def Main():
    if len(sys.argv) != 3:
        print("Usage: " + os.path.basename(sys.argv[0]) + " <bcPinSnoopRx> <bcPinSnoopTx>")
        sys.exit(-1)

    bcPinSnoopRx = int(sys.argv[1])
    bcPinSnoopTx = int(sys.argv[2])

    s = Snoop(bcPinSnoopRx, bcPinSnoopTx)

    Log("Waiting")
    evm_MainLoop()


Main()


