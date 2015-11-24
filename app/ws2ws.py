#!/usr/bin/python

import sys

from collections import deque

sys.path.append("../lib")
from libUtl import *
from libSimpleWsIface import *


class Bridge(WSNodeMgrEventHandlerIface):
    def __init__(self, urlFirst, urlSecond):
        WSNodeMgrEventHandlerIface.__init__(self)

        self.urlFirst  = urlFirst
        self.urlSecond = urlSecond
        self.wsNodeMgr = WSNodeMgr(self)

        self.handleSecond = None

        self.wsFirst  = None
        self.wsSecond = None

        self.timerHandle = None

        self.Start()

    def OnWebSocketConnectedOutbound(self, ws, userData):
        if userData == self.urlFirst:
            Log("Connection Established to First, "
                "starting connection to Second")

            self.wsFirst = ws

            self.handleSecond = self.wsNodeMgr.connect(self.urlSecond)
        else:
            Log("Connection Established to Second, Bridge Established")

            self.wsSecond = ws

            self.bridgeEstablished = True

            self.wsFirst.SetUserData(self.wsSecond)
            self.wsSecond.SetUserData(self.wsFirst)

            # flush queued data
            Log("    Flushing " + \
                str(len(self.msgQueue)) + \
                " queued messages from First to Second")
            for msg in self.msgQueue:
                self.wsSecond.Write(msg)

            self.msgQueue.clear()

    def OnWebSocketReadable(self, ws, userData):
        msg = ws.Read()

        if self.bridgeEstablished:
            ws.GetUserData().Write(msg)
        else:
            self.msgQueue.append(msg)

    def OnWebSocketClosed(self, ws, userData):
        side = "Second"
        if self.wsFirst == ws:
            side = "First"
        Log("Socket Closed by " + side + ", shutting down and starting over")

        self.Restart()

    def OnWebSocketError(self, ws, userData):
        side = "Second"
        if self.urlFirst == userData:
            side = "First"
        Log("Connection Refused by " + \
            side + \
            ", shutting down and starting over")

        self.Restart()

    def Start(self):
        msDelay = 0
        self.Restart(msDelay)

    def Restart(self, msDelay=5000):
        if not self.timerHandle:
            def OnTimeout():
                self.timerHandle = None
                self.RestartInternal()
            self.timerHandle = evm_SetTimeout(OnTimeout, msDelay)

    def RestartInternal(self):
        if self.handleSecond:
            self.wsNodeMgr.connect_cancel(self.handleSecond)
        if self.wsFirst:
            self.wsFirst.Close()
        if self.wsSecond:
            self.wsSecond.Close()

        self.bridgeEstablished = False

        self.handleSecond = None

        self.wsFirst  = None
        self.wsSecond = None

        self.msgQueue = deque()

        Log("")
        Log("Attempting to connect to First")
        handle = self.wsNodeMgr.connect(self.urlFirst, self.urlFirst)


def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <urlFirst> <urlSecond>")
        sys.exit(-1)

    urlFirst  = sys.argv[1]
    urlSecond = sys.argv[2]

    Log("Bridge Started: (" + urlFirst + ", " + urlSecond + ")")
    Bridge(urlFirst, urlSecond)

    evm_MainLoop()


Main()
