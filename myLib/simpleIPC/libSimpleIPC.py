#!/usr/bin/python

import sys
import os
import time

from struct import *
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.rfLink import *


class SimpleIPCMessage():
    def __init__(self, byteList):
        self.byteList = byteList

        if not self.byteList:
            self.byteList = bytearray()
            self.byteList.extend([0] * self.MESSAGE_SIZE)

        if hasattr(self, "MESSAGE_TYPE"):
            self.messageType = self.MESSAGE_TYPE

    def SetMessageType(self, messageType):
        self.messageType = messageType

    def GetMessageType(self):
        return self.messageType

    def GetByteList(self):
        return self.byteList



class SimpleIPCProtocolHandler():
    PROTOCOL_ID = 1

    def __init__(self):
        # Keep a list of message handlers
        self.msgHandlerList = deque()

    def RegisterSerialLink(self, serialLink):
        self.link = serialLink
        self.linkType = "SERIAL"

        self.link.SetCbOnRxAvailable(self.OnRx)

    def RegisterRFLink(self, rfLink):
        self.link = rfLink
        self.linkType = "RF"

        self.link.SetCbOnRxAvailable(self.OnRx)

    def RegisterRFLinkDefaultAddressing(self, realm, srcAddr):
        self.realm   = realm
        self.srcAddr = srcAddr

    def Send(self, dstAddr, msg):
        byteList = bytearray()

        byteList.extend([0] * 2)
        byteList[0:2] = pack("!H", msg.GetMessageType())

        byteList.extend(msg.GetByteList())

        if self.linkType == "SERIAL":
            # SerialLink doesn't need addressing -- ignore
            self.link.Send(self.PROTOCOL_ID, byteList)
        elif self.linkType == "RF":
            # RFLink requires addressing, so fill out header
            hdr = RFLinkHeader()
            hdr.SetRealm(self.realm)
            hdr.SetSrcAddr(self.srcAddr)
            hdr.SetDstAddr(dstAddr)
            hdr.SetProtocolId(self.PROTOCOL_ID)

            self.link.Send(hdr, byteList)

    def RegisterProtocolMessageHandler(self, handler):
        self.msgHandlerList.append(handler)

    def OnRx(self, hdr, byteList):
        if len(byteList) >= 2 and hdr.GetProtocolId() == 1:
            msg = SimpleIPCMessage(byteList[2:])
            msg.SetMessageType(*unpack("!H", buffer(byteList, 0, 2)))

            if self.linkType == "SERIAL":
                # Fake an RFLink header
                hdr = RFLinkHeader()
                hdr.SetRealm(0)
                hdr.SetSrcAddr(0)
                hdr.SetDstAddr(0)
                hdr.SetProtocolId(self.PROTOCOL_ID)

                self.OnSimpleIPCMsg(hdr, msg)
            elif self.linkType == "RF":
                self.OnSimpleIPCMsg(hdr, msg)

    def OnSimpleIPCMsg(self, srcAddr, msg):
        # offer to each handler until first one takes it
        for msgHandler in self.msgHandlerList:
            if msgHandler.HandleMessage(srcAddr, msg):
                break







