#!/usr/bin/python

import sys

from collections import deque

from libUtl import *
from libSimpleWsIface import *


class Bridge(WSNodeMgrEventHandlerIface):
    def __init__(self, urlFirst, urlSecond):
        self.urlFirst  = urlFirst
        self.urlSecond = urlSecond
        self.wsNodeMgr = WSNodeMgr(self)

        self.restarting = False

        self.Restart()

    def OnWebSocketConnectedOutbound(self, ws, userData):
        if userData == self.urlFirst:
            self.wsFirst = ws

            self.wsNodeMgr.connect(self.urlSecond)
        else:
            self.wsSecond = ws

            self.bridgeEstablished = True

            self.wsFirst.SetUserData(self.wsSecond)
            self.wsSecond.SetUserData(self.wsFirst)

            # flush queued data
            for msg in self.msgQueue:
                self.wsSecond.Send(msg)

            self.msgQueue.clear()

    def OnWebSocketReadable(self, ws, userData):
        msg = ws.Read()

        if self.bridgeEstablished:
            ws.GetUserData().Send(msg)
        else:
            self.msgQueue.append(msg)

    def OnWebSocketClosed(self, ws, userData):
        self.Restart()

    def OnWebSocketError(self, ws, userData):
        self.Restart()

    def Restart(self, msDelay=0):
        if self.restarting:
            return

        self.restarting = True
        if self.wsFirst:
            self.wsFirst.Close()
        if self.wsSecond:
            self.wsSecond.Close()
        self.restarting = False

        self.bridgeEstablished = False

        self.wsFirst  = None
        self.wsSecond = None

        self.msgQueue = deque()

        self.wsNodeMgr.connect(self.urlFirst, self.urlFirst)


def Main():
    HandleSignals()

    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <urlFirst> <urlSecond>")
        sys.exit(-1)

    urlFirst  = sys.argv[1]
    urlSecond = sys.argv[2]

    Bridge(urlFirst, urlSecond)

    evm_MainLoop()


Main()
