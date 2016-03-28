#!/usr/bin/python

import sys
import os
import time
from collections import deque

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.serial import *
from myLib.simpleIPC import *


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

    # Create SerialLink
    serialLink = SerialLink()
    serialLink.Init(bcPinRx, bcPinTx)

    # Create ProtocolHandler
    ph = SimpleIPCProtocolHandler(serialLink)

    # Create MessageHandler and associate ProtocolHandler
    msgHandler = SimpleIPCMessageHandlerTest(ph)

    # Register MessageHandler with ProtocolHandler
    ph.RegisterProtocolMessageHandler(msgHandler)

    Log("Waiting")
    evm_MainLoop()


Main()


