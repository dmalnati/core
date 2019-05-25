import sys
import os

from collections import deque




########################################################################
#
# WSBridge
#
########################################################################


class WSBridge(WSNodeMgrEventHandlerIface):
    def __init__(self, urlFirst, urlSecond):
        WSNodeMgrEventHandlerIface.__init__(self)

        self.urlFirst  = urlFirst
        self.urlSecond = urlSecond
        self.wsNodeMgr = WSNodeMgr(self)

        self.bridgeEstablished = False

        self.handleSecond = None

        self.wsFirst  = None
        self.wsSecond = None

        self.ws__ws = {}

        self.timerHandle = None

    ##########################################################
    #
    # Callback functions designed for an inheriting class
    #
    ##########################################################

    def OnStartOrRestart(self):
        pass

    def OnBridgeCommsUpFirst(self):
        pass

    def OnBridgeCommsUpSecond(self):
        pass

    def OnBridgeUp(self):
        pass

    def OnBeginFlushQueuedMessagesFromFirstToSecond(self, msgQueue):
        pass

    def OnEndFlushQueuedMessagesFromFirstToSecond(self):
        pass

    def OnBridgeCommsDownFirst(self):
        pass

    def OnBridgeCommsDownSecond(self):
        pass

    def OnBridgeCommsErrorFirst(self):
        pass

    def OnBridgeCommsErrorSecond(self):
        pass

    def OnBridgeDown(self):
        pass

    def OnMessageFromFirstToSecond(self, msg):
        return msg

    def OnMessageFromSecondToFirst(self, msg):
        return msg


    ##########################################################
    #
    # Functions specific to operating as a WS Bridge
    #
    ##########################################################

    def GetUrlFirst(self):
        return self.urlFirst

    def GetUrlSecond(self):
        return self.urlSecond

    def GetWsFirst(self):
        return self.wsFirst

    def GetWsSecond(self):
        return self.wsSecond

    def Start(self):
        msDelay = 0
        self.Restart(msDelay)

    def Restart(self, msDelay=5000):
        if not self.timerHandle:
            if self.bridgeEstablished:
                self.OnBridgeDown()

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

        self.ws__ws = {}

        self.msgQueue = deque()

        self.OnStartOrRestart()
        handle = self.wsNodeMgr.connect(self.urlFirst, self.urlFirst)


    ##########################################################
    #
    # Implementing the interface of the handler
    #
    ##########################################################

    def OnWebSocketConnectedOutbound(self, ws, userData):
        if userData == self.urlFirst:
            self.wsFirst = ws

            self.OnBridgeCommsUpFirst()

            self.handleSecond = self.wsNodeMgr.connect(self.urlSecond)
        else:
            self.wsSecond = ws

            self.OnBridgeCommsUpSecond()

            self.bridgeEstablished = True

            self.OnBridgeUp()

            # associate each ws with each other
            # intentionally don't use the ws userData so that inheriting
            # classes can if they want
            self.ws__ws[self.wsFirst] = self.wsSecond
            self.ws__ws[self.wsSecond] = self.wsFirst

            # flush queued data
            self.OnBeginFlushQueuedMessagesFromFirstToSecond(self.msgQueue)
            for msg in self.msgQueue:
                msgMaybeModifiedOrNone = self.OnMessageFromFirstToSecond(msg)
                if msgMaybeModifiedOrNone != None:
                    self.wsSecond.Write(msgMaybeModifiedOrNone)

            self.msgQueue.clear()
            self.OnEndFlushQueuedMessagesFromFirstToSecond()

    def OnWebSocketReadable(self, ws, userData):
        msg = ws.Read()

        if self.bridgeEstablished:
            msgMaybeModifiedOrNone = None

            if ws == self.wsFirst:
                msgMaybeModifiedOrNone = self.OnMessageFromFirstToSecond(msg)
            else:
                msgMaybeModifiedOrNone = self.OnMessageFromSecondToFirst(msg)

            if msgMaybeModifiedOrNone != None:
                self.ws__ws[ws].Write(msgMaybeModifiedOrNone)
        else:
            self.msgQueue.append(msg)

    def OnWebSocketClosed(self, ws, userData):
        if self.wsFirst == ws:
            self.OnBridgeCommsDownFirst()
        else:
            self.OnBridgeCommsDownSecond()

        self.Restart()

    def OnWebSocketError(self, ws, userData):
        if self.urlFirst == userData:
            self.OnBridgeCommsErrorFirst()
        else:
            self.OnBridgeCommsErrorSecond()

        self.Restart()










########################################################################
#
# WSBridgeLogger
#
########################################################################

class WSBridgeLoggerIface():
    def __init__(self):
        pass

    def OnStartOrRestart(self):
        Log("")
        Log("")
        Log("Attemping to bridge the following endpoints:")
        Log("    First : " + self.GetUrlFirst())
        Log("    Second: " + self.GetUrlSecond())
        Log("")
        Log("Attempting to connect to First")

    def OnBridgeCommsUpFirst(self):
        Log("Connection Established to First")
        Log("Attempting to connect to Second")

    def OnBridgeCommsUpSecond(self):
        Log("Connection Established to Second")

    def OnBridgeUp(self):
        Log("Bridge Established")

    def OnBeginFlushQueuedMessagesFromFirstToSecond(self, msgQueue):
        Log("    Flushing " + \
            str(len(msgQueue)) + \
            " queued messages from First to Second")

    def OnEndFlushQueuedMessagesFromFirstToSecond(self):
        Log("End of flushing")

    def OnBridgeCommsDownFirst(self):
        Log("Socket Closed by First")

    def OnBridgeCommsDownSecond(self):
        Log("Socket Closed by Second")

    def OnBridgeCommsErrorFirst(self):
        Log("Connection refused by First")

    def OnBridgeCommsErrorSecond(self):
        Log("Connection refused by Second")

    def OnBridgeDown(self):
        Log("Bridge Down, starting over")

    def OnMessageFromFirstToSecond(self, msg):
        Log("First  ==> Second (" + msg + ")")
        return msg

    def OnMessageFromSecondToFirst(self, msg):
        Log("Second ==> First  (" + msg + ")")
        return msg


