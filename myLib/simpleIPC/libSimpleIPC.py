#!/usr/bin/python

import sys
import os
import time
import re
import inspect

from struct import *
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.rfLink import *


class SimpleIPCMessage(object):
    def __init__(self, byteList):
        self.byteList = byteList

        if not self.byteList:
            self.byteList = bytearray()
            self.byteList.extend([0] * self.MESSAGE_SIZE)

        if hasattr(self, "MESSAGE_TYPE"):
            self.messageType = self.MESSAGE_TYPE

    @classmethod
    def GetClassModulePretty(cls):
        return str(cls.__module__).split(".")[-1][24:]

    @classmethod
    def GetClassName(cls):
        return cls.__name__

    @classmethod
    def GetClass(cls):
        return cls

    def SetMessageType(self, messageType):
        self.messageType = messageType

    def GetMessageType(self):
        return self.messageType

    def GetMessageSize(self):
        return self.MESSAGE_SIZE

    def GetByteList(self):
        return self.byteList

    def Print(self):
        # find list of Getters
        getterList = []

        # get attrs in order the hard way
        for line in inspect.getsource(self.__class__).split("\n"):
            m = re.match(r"^ *def (Get.+)\(.*", line)

            if m:
                attr = m.group(1)

                if attr != "GetByteList" and \
                   attr != "GetMessageSize" and \
                   attr != "GetMessageType" and \
                   attr != "GetClassName" and \
                   attr != "GetClassModulePretty":
                    getterList.append(attr[3:])

        # determine max length for formatting purposes
        maxLen = 0
        for getter in getterList:
            if len(getter) > maxLen:
                maxLen = len(getter)

        # create format string
        formatStr = "    %-" + str(maxLen) + "s: %s"

        # Actually print
        print(self.GetClassName() + "[" + str(self.GetMessageType()) + "]")
        if len(getterList):
            for getter in getterList:
                fn = getattr(self, "Get" + getter)
                val = str(fn())

                print(formatStr % (getter, val))
        else:
            print("    [no fields]")



class SimpleIPCProtocolHandler():
    PROTOCOL_ID = 1

    def __init__(self):
        # Keep a list of message handlers
        self.msgHandlerList = deque()

        # Keep handle to underlying link type when event driven
        self.linkType = None

    def PrintState(self):
        self.PrintMessageTypes()
        self.PrintMessageHandlerSupport()

    def HandlerCanHandleMsg(self, msgHandler, msg):
        return ("OnHandle%s" % msg.GetClassName()) in dir(msgHandler)

    def HandlerCanHandleUnknownMsg(self, msgHandler):
        return "OnHandleUnknownMessage" in dir(msgHandler)

    def GetSimpleIPCMessageClassList(self):
        return SimpleIPCMessage.__subclasses__()

    def PrintMessageHandlerSupport(self):
        print("%i Installed Message Handlers:" % len(self.msgHandlerList))
        i = 1
        for msgHandler in self.msgHandlerList:
            print("    %i - %s" % (i, msgHandler.__class__.__name__))
            ++i

        print("")

        # print support for each message type by each handler
        print("Handler Support by Module and MessageType:")
        modulePrettyLast = None
        for sc in self.GetSimpleIPCMessageClassList():
            # build handler support string
            supportedStr = ""
            i = 1
            for msgHandler in self.msgHandlerList:
                if self.HandlerCanHandleMsg(msgHandler, sc):
                    supportedStr += str(i)
                else:
                    supportedStr += " "
                ++i

            # print support by message
            modulePretty = sc.GetClassModulePretty()
            if modulePretty != modulePrettyLast:
                print("%s:" % modulePretty)
                modulePrettyLast = modulePretty

            print("    %s : %s" % (supportedStr, sc.GetClassName()))

        # print support for the unknown message type handler
        print("[DefaultMessageHandler]:")
        supportedStr = ""
        i = 1
        for msgHandler in self.msgHandlerList:
            if self.HandlerCanHandleUnknownMsg(msgHandler):
                supportedStr += str(i)
            else:
                supportedStr += " "
            ++i

        # print support by message
        print("    %s : %s" % (supportedStr, "[DefaultMessageHandler]"))

        print("")

    def PrintMessageTypes(self):
        print("MessageType by Module:")
        scList = self.GetSimpleIPCMessageClassList()

        parentModuleStrPrettyLast = None
        for sc in scList:
            # get pretty version of class module
            parentModuleStrPretty = sc.GetClassModulePretty()

            # print out module if haven't yet for this group of classes
            if parentModuleStrPretty != parentModuleStrPrettyLast:
                print("%s" % parentModuleStrPretty)
                parentModuleStrPrettyLast = parentModuleStrPretty

            # print out class
            print("    [%3i] %s" % (sc.MESSAGE_TYPE, sc.GetClassName()))

        print("")

    def RegisterSerialLink(self, serialLink):
        self.link = serialLink
        self.linkType = "SERIAL"

        self.link.SetCbOnRxAvailable(self.OnRx)

    def RegisterRFLink(self, rfLink):
        self.link = rfLink
        self.linkType = "RF"

        self.link.SetCbOnRxAvailable(self.OnRx)

    def RegisterRFLinkDefaultAddressing(self, realm, srcAddr):
        self.realm   = realm
        self.srcAddr = srcAddr

    def Send(self, dstAddr, msg):
        byteList = bytearray()

        byteList.extend([0] * 2)
        byteList[0:2] = pack("!H", msg.GetMessageType())

        byteList.extend(msg.GetByteList())

        if self.linkType == "SERIAL":
            # SerialLink doesn't need addressing -- ignore
            self.link.Send(self.PROTOCOL_ID, byteList)
        elif self.linkType == "RF":
            # RFLink requires addressing, so fill out header
            hdr = RFLinkHeader()
            hdr.SetRealm(self.realm)
            hdr.SetSrcAddr(self.srcAddr)
            hdr.SetDstAddr(dstAddr)
            hdr.SetProtocolId(self.PROTOCOL_ID)

            self.link.Send(hdr, byteList)

    def RegisterProtocolMessageHandler(self, handler):
        self.msgHandlerList.append(handler)

    def ParseSimpleIPCData(self, hdrMaybeRFLink, byteList):
        retVal = None

        if len(byteList) >= 2 and hdrMaybeRFLink.GetProtocolId() == 1:
            msg = SimpleIPCMessage(byteList[2:])
            msg.SetMessageType(*unpack("!H", buffer(byteList, 0, 2)))

            hdrRFLink = None
            if self.linkType == "SERIAL" or self.linkType == None:
                # Fake an RFLink header
                hdrRFLink = RFLinkHeader()
                hdrRFLink.SetRealm(0)
                hdrRFLink.SetSrcAddr(0)
                hdrRFLink.SetDstAddr(0)
                hdrRFLink.SetProtocolId(self.PROTOCOL_ID)

                retVal = (hdrRFLink, msg)
            elif self.linkType == "RF":
                hdrRFLink = hdrMaybeRFLink
                retVal = (hdrRFLink, msg)

        return retVal

    def OnRx(self, hdrMaybeRFLink, byteList):
        hdrAndByteList = self.ParseSimpleIPCData(hdrMaybeRFLink, byteList)

        if hdrAndMsg:
            (hdr, msg) = hdrAndMsg

            self.OnSimpleIPCMsg(hdr, msg)


    def ParseSimpleIPCMessage(self, msg):
        retVal = None

        # identify message
        for msgClass in self.GetSimpleIPCMessageClassList():
            if msgClass.MESSAGE_TYPE == msg.GetMessageType():
                # message type identified.
                # construct actual class to contain message.
                msgParsed = msgClass(msg.GetByteList())

                retVal = msgParsed

                break

        return retVal

    def OnSimpleIPCMsg(self, hdr, msg):
        msgParsed = self.ParseSimpleIPCData(msg)

        if msgParsed:
            msgClass = msgParsed.GetClass()

            # offer to each handler which can handle it
            for msgHandler in self.msgHandlerList:
                if self.HandlerCanHandleMsg(msgHandler, msgClass):
                    # get a handle to the function
                    fn = \
                        getattr(msgHandler, \
                                ("OnHandle%s" % msgClass.GetClassName()))

                    # call it
                    fn(hdr, msgParsed)


