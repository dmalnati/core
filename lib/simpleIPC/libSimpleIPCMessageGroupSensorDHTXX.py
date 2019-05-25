#!/usr/bin/python

import sys
import os
import time
from collections import deque



class MessageReqGetTemperature(SimpleIPCMessage):
    MESSAGE_TYPE = 10
    MESSAGE_SIZE = 0

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)


class MessageRepGetTemperature(SimpleIPCMessage):
    MESSAGE_TYPE = 11
    MESSAGE_SIZE = 4

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)

    def GetTempF(self):
        return unpack("B", buffer(self.byteList, 0, 1))[0]

    def SetTempF(self, value):
        self.byteList[0] = pack("B", int(value))

    def GetTempC(self):
        return unpack("B", buffer(self.byteList, 1, 1))[0]

    def SetTempC(self, value):
        self.byteList[1] = pack("B", int(value))

    def GetPctHumidity(self):
        return unpack("B", buffer(self.byteList, 2, 1))[0]

    def SetPctHumidity(self, value):
        self.byteList[2] = pack("B", int(value))

    def GetHeatIndex(self):
        return unpack("B", buffer(self.byteList, 3, 1))[0]

    def SetHeatIndex(self, value):
        self.byteList[3] = pack("B", int(value))

