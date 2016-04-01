#!/usr/bin/python

import sys
import os
import time
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from libSimpleIPC import *


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

    def GetTempC(self):
        return unpack("B", buffer(self.byteList, 1, 1))[0]

    def GetPctHumidity(self):
        return unpack("B", buffer(self.byteList, 2, 1))[0]

    def GetHeatIndex(self):
        return unpack("B", buffer(self.byteList, 3, 1))[0]


