#!/usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.serial import *
from myLib.rfLink import *
from .libSimpleIPC import *
from .libSimpleIPCShell import *



class SimpleIPCManager():
    def __init__(self, \
                 bcPinRx, \
                 bcPinTx, \
                 realm=None, \
                 srcAddr=None, \
                 dstAddr=None):

        # Get SerialLink, and RFLink to sit on top of it if configured
        self.serialLink = SerialLink(bcPinRx, bcPinTx)

        if realm != None and srcAddr != None  and dstAddr != None:
            self.rfLink = RFLinkOverSerial(self.serialLink)

        # Create ProtocolHandler and set up default addressing
        self.ph = SimpleIPCProtocolHandler()

        if realm != None and srcAddr != None  and dstAddr != None:
            self.ph.RegisterRFLink(self.rfLink)
            self.ph.RegisterRFLinkDefaultAddressing(realm, srcAddr, dstAddr)
        else:
            self.ph.RegisterSerialLink(self.serialLink)

    def RunInteractiveShell(self):
        # Create a shell
        sh = SimpleIPCShell(self.ph)

        # Have the shell handle all inbound messages
        self.ph.RegisterProtocolMessageHandler(sh)

    def GetProtocolHandler(self):
        return self.ph

    def RegisterProtocolMessageHandler(self, handler):
        self.ph.RegisterProtocolMessageHandler(handler)

