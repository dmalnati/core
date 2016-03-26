#!/usr/bin/python

import sys
import os
import time
from collections import deque

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.serial import *



from struct import *
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

    def __init__(self, bcPinRx, bcPinTx):
        # Get a SerialLink
        self.serialLink = SerialLink()

        self.serialLink.Init(bcPinRx, bcPinTx, self.OnRx)

        # Keep a list of message handlers
        self.msgHandlerList = deque()

    def Send(self, msg):
        byteList = bytearray()

        byteList.extend([0] * 2)
        byteList[0:2] = pack("!H", msg.GetMessageType())

        byteList.extend(msg.GetByteList())

        Log("Sending:")
        for byte in byteList:
            Log(("  %3i" % byte))

        self.serialLink.Send(self.PROTOCOL_ID, byteList)

    def RegisterProtocolMessageHandler(self, handler):
        self.msgHandlerList.append(handler)

    def OnRx(self, hdr, byteList):
        Log("OnRx")
        for byte in byteList:
            Log(("  %3i" % byte))

        if len(byteList) >= 2 and hdr.GetProtocolId() == 1:
            msg = SimpleIPCMessage(byteList[2:])
            msg.SetMessageType(*unpack("!H", buffer(byteList, 0, 2)))

            self.OnSimpleIPCMsg(msg)

    def OnSimpleIPCMsg(self, msg):
        # offer to each handler until first one takes it
        for msgHandler in self.msgHandlerList:
            if msgHandler.HandleMessage(msg):
                break



###################################################################

class MessageGetPinState(SimpleIPCMessage):
    MESSAGE_TYPE = 1
    MESSAGE_SIZE = 1

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)

    def SetPin(self, pin):
        self.byteList[0] = pack("B", int(pin))

class MessageSetPinState(SimpleIPCMessage):
    MESSAGE_TYPE = 2
    MESSAGE_SIZE = 2

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)

    def SetPin(self, pin):
        self.byteList[0] = pack("B", int(pin))

    def SetValue(self, value):
        self.byteList[1] = pack("B", int(value))

class MessagePinState(SimpleIPCMessage):
    MESSAGE_TYPE = 3
    MESSAGE_SIZE = 2

    def __init__(self, byteList = None):
        SimpleIPCMessage.__init__(self, byteList)

    def GetPin(self):
        return unpack("B", buffer(self.byteList, 0, 1))

    def GetValue(self):
        return unpack("B", buffer(self.byteList, 1, 1))




class SimpleIPCMessageHandlerTest():
    def __init__(self, protocolHandler):
        self.ph = protocolHandler

        WatchStdinEndLoopOnEOF(self.OnStdin)

    def HandleMessage(self, msg):
        # we'll accept anything, just testing
        Log("Type %3i" % msg.GetMessageType())
        byteList = msg.GetByteList()
        for byte in byteList:
            Log(("  %3i" % byte))

        if msg.GetMessageType() == MessagePinState.MESSAGE_TYPE:
            Log("It's recognized!")
            msg = MessagePinState(byteList)
            Log("Pin  : %3i" % msg.GetPin())
            Log("Value: %3i" % msg.GetValue())

        return True

    def OnStdin(self, line):
        # look for:
        # set <pinNumber> <1=on,0=off>
        # get <pinNumber>

        wordList = line.split()
        wordListLen = len(wordList)

        if wordListLen == 3 and wordList[0] == "set":
            pinNumber = int(wordList[1])
            pinValue  = int(wordList[2])

            Log("set %i %i" % (pinNumber, pinValue))

            msg = MessageSetPinState()
            msg.SetPin(pinNumber)
            msg.SetValue(pinValue)

            self.ph.Send(msg)

        elif wordListLen == 2 and wordList[0] == "get":
            pinNumber = int(wordList[1])

            Log("get %i" % pinNumber)

            msg = MessageGetPinState()
            msg.SetPin(pinNumber)

            self.ph.Send(msg)

        else:
            Log("Command not understood: " + line)


###################################################################

def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <bcPinRx> <bcPinTx>")
        sys.exit(-1)

    bcPinRx = int(sys.argv[1])
    bcPinTx = int(sys.argv[2])

    ph = SimpleIPCProtocolHandler(bcPinRx, bcPinTx)

    msgHandler = SimpleIPCMessageHandlerTest(ph)

    ph.RegisterProtocolMessageHandler(msgHandler)

    Log("Waiting")
    evm_MainLoop()


Main()


