#!/usr/bin/python

import sys
import os
import time

from struct import *
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


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

    def __init__(self, link):
        self.link = link

        self.link.SetCbOnRxAvailable(self.OnRx)

        # Keep a list of message handlers
        self.msgHandlerList = deque()

    def Send(self, msg):
        byteList = bytearray()

        byteList.extend([0] * 2)
        byteList[0:2] = pack("!H", msg.GetMessageType())

        byteList.extend(msg.GetByteList())

        self.link.Send(self.PROTOCOL_ID, byteList)

    def RegisterProtocolMessageHandler(self, handler):
        self.msgHandlerList.append(handler)

    def OnRx(self, hdr, byteList):
        if len(byteList) >= 2 and hdr.GetProtocolId() == 1:
            msg = SimpleIPCMessage(byteList[2:])
            msg.SetMessageType(*unpack("!H", buffer(byteList, 0, 2)))

            self.OnSimpleIPCMsg(msg)

    def OnSimpleIPCMsg(self, msg):
        # offer to each handler until first one takes it
        for msgHandler in self.msgHandlerList:
            if msgHandler.HandleMessage(msg):
                break







