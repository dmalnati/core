#!/usr/bin/python

import json
import sys

from libUtl import *
from libSimpleWsIface import *


def SetUpTimer(msTimeout):
    print("Setting up interval timer for " + str(msTimeout) + "ms")

    def Timeout():
        Log("Timeout")

    evm_PeriodicCallback(Timeout, msTimeout)




class Handler(WSNodeMgrEventHandlerIface):
    def OnWebSocketCreated(self, ws, userData):
        Log("created: " + userData)

    def OnWebSocketReadable(self, ws, userData):
        Log("readable: " + userData)

    def OnWebSocketClosed(self, ws, userData):
        Log("closed: " + userData)

    def OnWebSocketError(self, ws, userData):
        Log("error: " + userData)




def OnStdin(line):
    print("stdin: " + line)


def Main():
    url = sys.argv[1]

    HandleSignals()
    HandleStdin(OnStdin)

    SetUpTimer(1000)

    print ("Connecting to url: " + url)

    handler = Handler()
    wsNodeMgr = WSNodeMgr(handler)


    wsNodeMgr.connect(url, "auto1")


    evm_MainLoop()


Main()
