#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.serial import *


class SerialLinkBridge():
    def __init__(self, bcPinRx, bcPinTx, protocolId):
        self.protocolId = protocolId
        
        # Create buffer for inbound data
        self.byteList = bytearray()

        # Get a SerialLink
        self.serialLink = SerialLink(bcPinRx, bcPinTx)
        
        # Register to receive data
        self.serialLink.SetCbOnRxAvailable(self.OnRx)

    def OnRx(self, hdr, byteList):
        Log("HDR: %i bytes" % hdr.GetSize())
        Log("  Preamble  : %3i" % hdr.GetPreamble())
        Log("  DataLength: %3i" % hdr.GetDataLength())
        Log("  Checksum  : %3i" % hdr.GetChecksum())
        Log("  ProtocolId: %3i" % hdr.GetProtocolId())

        count = len(byteList)
        
        Log("MSG: %i bytes" % count)

        for byte in byteList:
            Log(("  %3i (%02X)" % (byte, byte)))

        print("")
    
    def OnBinaryData(self, byteList):
        self.byteList.extend(byteList)
        
        self.ParseBuffer()
        
    # Expecting:
    # - dataLen  - count of number of bytes of actual payload, not including
    #              this parameter itself
    # - byteList - the 'dataLen' number of bytes
    def ParseBuffer(self):
        cont = True
    
        while cont:
            byteListLen = len(self.byteList)
            
            if byteListLen:
                dataLenValue = self.byteList[0]
                
                availableBytesInBuffer = byteListLen - 1
                
                # Check if enough bytes available to extract the message
                if (dataLenValue <= availableBytesInBuffer):
                    # Copy the message, excluding the length byte
                    buf = self.byteList[1:dataLenValue+1]
                    
                    # Remove used bytes from buffer
                    del self.byteList[0:dataLenValue+1]
                    
                    # Send extracted message
                    self.serialLink.Send(self.protocolId, buf)
                else:
                    cont = False
            else:
                cont = False

def Main():
    if len(sys.argv) != 4:
        print("Usage: " + sys.argv[0] + " <bcPinRx> <bcPinTx> <protocolId>")
        sys.exit(-1)

    bcPinRx = sys.argv[1]
    bcPinRx = None if bcPinRx == "-" else int(bcPinRx)
    bcPinTx = sys.argv[2]
    bcPinTx = None if bcPinTx == "-" else int(bcPinTx)
    protocolId = int(sys.argv[3])

    slb = SerialLinkBridge(bcPinRx, bcPinTx, protocolId)
    
    WatchStdinEndLoopOnEOF(slb.OnBinaryData, binary=True)

    Log("Waiting")
    evm_MainLoop()


Main()


