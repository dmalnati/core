#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *





# slightly re-arranged from code found here:
# http://www.evilgeniuslair.com/2015/01/14/crc-8/
import binascii
class CRC8:
    def __init__(self):
        pass

    @staticmethod
    def Calculate(buf):
        return CRC8.calcCheckSum(buf)

    @staticmethod
    def calcCheckSum(incoming):
        #msgByte = hexStr2Byte(incoming)
        msgByte = bytearray(incoming)
        check = 0
        for i in msgByte:
            check = CRC8.AddToCRC(i, check)
        return check

    @staticmethod
    def AddToCRC(b, crc):
        b2 = b
        if (b < 0):
            b2 = b + 256
        for i in xrange(8):
            odd = ((b2^crc) & 1) == 1
            crc >>= 1
            b2 >>= 1
            if (odd):
                crc ^= 0x8C # this means crc ^= 140
        return crc





class SerialLinkHeader():
    def __init__(self, data, reserve = False):
        self.data = data

        if reserve:
            self.data.extend([0] * 4)

    @staticmethod
    def GetSize():
        return 4

    def SetPreamble(self, preamble):
        self.data[0] = preamble

    def GetPreamble(self):
        return self.data[0]

    def SetDataLength(self, dataLength):
        self.data[1] = dataLength

    def GetDataLength(self):
        return self.data[1]

    def SetChecksum(self, checksum):
        self.data[2] = checksum

    def GetChecksum(self):
        return self.data[2]

    def SetProtocolId(self, protocolId):
        self.data[3] = protocolId

    def GetProtocolId(self):
        return self.data[3]


class SerialLink():
    def __init__(self):
        self.BAUD              = 9600
        self.PREAMBLE_BYTE     = 0x55
        self.RX_POLL_PERIOD_MS = 100

        self.bcPinRx = None
        self.bcPinTx = None

        self.cbOnRxAvailable = None

        self.state = "LOOKING_FOR_PREAMBLE_BYTE"
        self.bufRx = bytearray()

        self.pigd = pigpio.pi()

    def Init(self, bcPinRx, bcPinTx, cbOnRxAvailable):
        self.bcPinRx = bcPinRx
        self.bcPinTx = bcPinTx

        self.cbOnRxAvailable = cbOnRxAvailable

        self.InitRx()
        self.InitTx()

    def InitRx(self):
        # open pin for reading serial
        pigpio.exceptions = False
        self.pigd.bb_serial_read_close(self.bcPinRx)
        pigpio.exceptions = True
        self.pigd.bb_serial_read_open(self.bcPinRx, self.BAUD)

        # set up timer to check on incoming data
        evm_SetTimeout(self.OnTimeoutCheckRx, self.RX_POLL_PERIOD_MS)

    def InitTx(self):
        pigpio.exceptions = False
        self.pigd.set_mode(self.bcPinTx, pigpio.OUTPUT)
        pigpio.exceptions = True

    def Send(self, protocolId, buf):
        # Create frame
        msg = bytearray() 

        # Fill out header
        hdr = SerialLinkHeader(msg, reserve = True)
        hdr.SetPreamble(self.PREAMBLE_BYTE)
        hdr.SetDataLength(len(buf))
        hdr.SetChecksum(0x00)
        hdr.SetProtocolId(protocolId)

        # Add data
        msg.extend(buf)

        # Calculate Checksum
        checksum = CRC8.Calculate(msg)

        # Update the message checksum now that it is calculated
        hdr.SetChecksum(checksum)

        # Create serial waveform
        self.pigd.wave_clear()
        self.pigd.wave_add_serial(self.bcPinTx, self.BAUD, msg)

        serialWave = self.pigd.wave_create()

        # Send serial data
        self.pigd.wave_send_once(serialWave)
        self.pigd.wave_delete(serialWave)

        # Wait for TX to complete
        while self.pigd.wave_tx_busy():
            pass

    def TryToSyncStreamFromSerial(self):
        (count, byteList) = self.pigd.bb_serial_read(self.bcPinRx)

        for byte in byteList:
            if self.state == "LOOKING_FOR_PREAMBLE_BYTE":
                if byte == 0x55:
                    self.bufRx.append(byte)
                    self.state = "LOOKING_FOR_END_OF_MESSAGE"
            elif self.state == "LOOKING_FOR_END_OF_MESSAGE":
                self.bufRx.append(byte)

    def TryToAddMoreDataFromSerial(self):
        # due to unfortunate way of reading from serial, and the way the
        # sync function is then implemented, calling the sync function is
        # what is needed here
        self.TryToSyncStreamFromSerial()

    def ClearLeadingBufferBytesAndRecalibrate(self, removeLen):
        bufRxSize = len(self.bufRx)

        if removeLen < bufRxSize:
            del self.bufRx[0:removeLen]

            # Search for preamble byte
            try:
                idx = self.bufRx.index(bytes(self.PREAMBLE_BYTE))

                # Shift all bytes to start of buffer
                del self.bufRx[0:idx]
                self.state = "LOOKING_FOR_END_OF_MESSAGE"
            except ValueError:
                # Couldn't find preamble
                bufRxSizeNew = len(self.bufRx)

                del self.bufRx[0:bufRxSizeNew]
                self.state = "LOOKING_FOR_PREAMBLE_BYTE"
        else:
            # Should never happen.  Zero out the buffer.
            del self.bufRx[0:bufRxSize]
            self.state = "LOOKING_FOR_PREAMBLE_BYTE"

    def TryToProcessMessageFromCachedData(self):
        bufRxSize = len(self.bufRx)

        if bufRxSize >= (SerialLinkHeader.GetSize()):
            hdr = SerialLinkHeader(self.bufRx)

            msgSize = SerialLinkHeader.GetSize() + hdr.GetDataLength()

            if bufRxSize >= msgSize:
                # keep a cached copy of the checksum since the current value
                # will be overwritten during validation
                checksumTmp = hdr.GetChecksum()

                # zero out message checksum for local calculation
                hdr.SetChecksum(0x00)

                # Calculate Checksum
                #crc = CRC8()
                checksum = CRC8.Calculate(self.bufRx[0:msgSize])

                # Restore the message checksum
                hdr.SetChecksum(checksumTmp)

                # Validate whether checksums match
                if (checksum == hdr.GetChecksum()):
                    self.cbOnRxAvailable(\
                        hdr, \
                        self.bufRx[SerialLinkHeader.GetSize():msgSize])

                    self.ClearLeadingBufferBytesAndRecalibrate(msgSize)
                else:
                    self.ClearLeadingBufferBytesAndRecalibrate(1)

    def OnTimeoutCheckRx(self):
        if self.state == "LOOKING_FOR_PREAMBLE_BYTE":
            self.TryToSyncStreamFromSerial()

        if self.state == "LOOKING_FOR_END_OF_MESSAGE":
            self.TryToAddMoreDataFromSerial()

            self.TryToProcessMessageFromCachedData()

        evm_SetTimeout(self.OnTimeoutCheckRx, self.RX_POLL_PERIOD_MS)



class TestSerialLink():
    def __init__(self, bcPinRx, bcPinTx):
        self.SEND_INTERVAL_MS = 2000

        # Get a SerialLink
        self.serialLink = SerialLink()
        self.serialLink.Init(bcPinRx, bcPinTx, self.OnRx)

        # Set up timer to periodically send data
        evm_SetTimeout(self.OnTimeoutTx, self.SEND_INTERVAL_MS)

    def OnRx(self, hdr, byteList):
        print("OnRx")

        Log("HDR: %i bytes" % hdr.GetSize())
        Log("  Preamble  : %3i" % hdr.GetPreamble())
        Log("  DataLength: %3i" % hdr.GetDataLength())
        Log("  Checksum  : %3i" % hdr.GetChecksum())
        Log("  ProtocolId: %3i" % hdr.GetProtocolId())

        count = len(byteList)
        Log("MSG: %i bytes" % count)
        for byte in byteList:
            Log(("  %3i" % byte))

    def OnTimeoutTx(self):
        protocolId = 1
        self.serialLink.Send(protocolId, "heynow")
        evm_SetTimeout(self.OnTimeoutTx, self.SEND_INTERVAL_MS)


def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <bcPinRx> <bcPinTx>")
        sys.exit(-1)

    bcPinRx = int(sys.argv[1])
    bcPinTx = int(sys.argv[2])

    tsl = TestSerialLink(bcPinRx, bcPinTx)

    Log("Waiting")
    evm_MainLoop()


Main()


