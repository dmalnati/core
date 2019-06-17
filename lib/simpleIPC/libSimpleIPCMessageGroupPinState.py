#!/usr/bin/python3.5 -u

import sys
import os
import time
from collections import deque



class MessageGetPinState(SimpleIPCMessage):
    MESSAGE_TYPE = 1
    MESSAGE_SIZE = 1

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)

    def GetPin(self):
        return unpack("B", buffer(self.byteList, 0, 1))[0]

    def SetPin(self, pin):
        self.byteList[0] = pack("B", int(pin))


class MessageSetPinState(SimpleIPCMessage):
    MESSAGE_TYPE = 2
    MESSAGE_SIZE = 2

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)

    def GetPin(self):
        return unpack("B", buffer(self.byteList, 0, 1))[0]

    def SetPin(self, pin):
        self.byteList[0] = pack("B", int(pin))

    def GetValue(self):
        return unpack("B", buffer(self.byteList, 1, 1))[0]

    def SetValue(self, value):
        self.byteList[1] = pack("B", int(value))


class MessagePinState(SimpleIPCMessage):
    MESSAGE_TYPE = 3
    MESSAGE_SIZE = 2

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)

    def GetPin(self):
        return unpack("B", buffer(self.byteList, 0, 1))[0]

    def SetPin(self, pin):
        self.byteList[0] = pack("B", int(pin))

    def GetValue(self):
        return unpack("B", buffer(self.byteList, 1, 1))[0]

    def SetValue(self, value):
        self.byteList[1] = pack("B", int(value))





