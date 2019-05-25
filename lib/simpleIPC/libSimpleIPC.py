#!/usr/bin/python

import sys
import os
import time
import re
import inspect

from struct import *
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from lib.utl import *
from lib.rfLink import *


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

    def Set(self, name, value):
        retVal = False

        for setter in self.GetSetterList():
            if setter == name:
                retVal = True

                fn = getattr(self, ("Set%s" % setter))

                # call it
                fn(value)

                break

        return retVal

    def GetSetterList(self):
        # find list of Setters
        setterList = []

        # get attrs in order the hard way
        for line in inspect.getsource(self.__class__).split("\n"):
            m = re.match(r"^ *def (Set.+)\(.*", line)

            if m:
                attr = m.group(1)
                setterList.append(attr[3:])

        return setterList

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
        print("[" + str(self.GetMessageType()) + "]" + self.GetClassName())
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

        # Set up default addressing if in RFLink mode
        self.realm   = 0
        self.srcAddr = 0
        self.dstAddr = 0

    def PrintAddr(self):
        if self.linkType == "SERIAL":
            print("SERIAL Addressing")
        elif self.linkType == "RF":
            print("RFLink Connection")

            hdr = RFLinkHeader()

            hdr.SetRealm(self.realm)
            hdr.SetSrcAddr(self.srcAddr)
            hdr.SetDstAddr(self.dstAddr)
            hdr.SetProtocolId(self.PROTOCOL_ID)

            hdr.Print()

    def PrintState(self):
        self.PrintMessageTypes()
        self.PrintMessageHandlerSupport()

    def HandlerCanHandleMsg(self, msgHandler, msg):
        return ("OnHandle%s" % msg.GetClassName()) in dir(msgHandler)

    def HandlerCanHandleUnknownMsg(self, msgHandler):
        return "OnHandleUnknownMessage" in dir(msgHandler)

    def TryToGetHandlerFn(self, msgHandler, msg):
        retVal = None

        if self.HandlerCanHandleMsg(msgHandler, msg):
            # get a handle to the function
            retVal = getattr(msgHandler, \
                             ("OnHandle%s" % msg.GetClassName()))
        elif self.HandlerCanHandleUnknownMsg(msgHandler):
            # get a handle to the function
            retVal = getattr(msgHandler, "OnHandleUnknownMessage")

        return retVal


    def GetSimpleIPCMessageClassList(self):
        return SimpleIPCMessage.__subclasses__()

    # Get an instance, not the class object
    def GetSimpleIPCMessageByMessageType(self, msgType):
        retVal = None

        for cls in self.GetSimpleIPCMessageClassList():
            if str(cls.MESSAGE_TYPE) == str(msgType):
                retVal = cls()

                break

        return retVal

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

    def RegisterRFLinkDefaultAddressing(self, realm, srcAddr, dstAddr):
        self.realm   = realm
        self.srcAddr = srcAddr
        self.dstAddr = dstAddr

    def Send(self, msg):
        self.SendToFull(self.realm, self.srcAddr, self.dstAddr, msg)

    def SendTo(self, dstAddr, msg):
        self.SendToFull(self.realm, self.srcAddr, dstAddr, msg)

    def SendToFrom(self, srcAddr, dstAddr, msg):
        self.SendToFull(self.realm, srcAddr, dstAddr, msg)

    def SendToFull(self, realm, srcAddr, dstAddr, msg):
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
            hdr.SetRealm(realm)
            hdr.SetSrcAddr(srcAddr)
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

        if hdrAndByteList:
            (hdr, msg) = hdrAndByteList

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
        msgParsed = self.ParseSimpleIPCMessage(msg)

        if msgParsed:
            msgClass = msgParsed.GetClass()

            # offer to each handler which can handle it
            for msgHandler in self.msgHandlerList:
                # try to get function to call
                fn = self.TryToGetHandlerFn(msgHandler, msgClass)

                if fn:
                    fn(hdr, msgParsed)










