#!/usr/bin/python3.5 -u

import sys
import os
import time



class RFLinkHeader():
    def __init__(self, byteList = None):
        self.byteList = byteList

        if not self.byteList:
            self.byteList = bytearray()
            self.byteList.extend([0] * RFLinkHeader.GetSize())

    @staticmethod
    def GetSize():
        return 4

    def GetByteList(self):
        return self.byteList

    def SetRealm(self, realm):
        self.byteList[0] = realm

    def GetRealm(self):
        return self.byteList[0]

    def SetSrcAddr(self, srcAddr):
        self.byteList[1] = srcAddr

    def GetSrcAddr(self):
        return self.byteList[1]

    def SetDstAddr(self, dstAddr):
        self.byteList[2] = dstAddr

    def GetDstAddr(self):
        return self.byteList[2]

    def SetProtocolId(self, protocolId):
        self.byteList[3] = protocolId

    def GetProtocolId(self):
        return self.byteList[3]

    def Print(self):
        print("RFLink Header:")
        print("    Realm     : %3i" % self.GetRealm())
        print("    SrcAddr   : %3i" % self.GetSrcAddr())
        print("    DstAddr   : %3i" % self.GetDstAddr())
        print("    ProtocolId: %3i" % self.GetProtocolId())


class RFLinkOverSerial():
    def __init__(self, serialLink):
        if serialLink:
            self.serialLink = serialLink

            self.serialLink.SetCbOnRxAvailable(self.OnRxAvailable)

            self.cbOnRxAvailable = None

    def SetCbOnRxAvailable(self, cbOnRxAvailable):
        self.cbOnRxAvailable = cbOnRxAvailable

    def ParseRFLinkData(self, serialHdr, serialByteList):
        retVal = None

        if len(serialByteList) >= RFLinkHeader.GetSize():
            rfHdr = RFLinkHeader(serialByteList[0:RFLinkHeader.GetSize()])

            rfByteList = serialByteList[RFLinkHeader.GetSize():]

            retVal = (rfHdr, rfByteList)

        return retVal

    def OnRxAvailable(self, serialHdr, serialByteList):
        rfHdrAndRfByteList = self.ParseRFLinkData(serialHdr, serialByteList)

        if rfHdrAndRfByteList:
            (rfHdr, rfByteList) = rfHdrAndRfByteList

            self.cbOnRxAvailable(rfHdr, rfByteList)

    def Send(self, rfHdr, rfByteList):
        serialByteList = bytearray()

        serialByteList.extend(rfHdr.GetByteList())
        serialByteList.extend(rfByteList)

        # protocol 0 == raw data, pass-through
        self.serialLink.Send(0, serialByteList)

            


