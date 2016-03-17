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

    def Calculate(self, buf):
        return self.calcCheckSum(buf)

    def calcCheckSum(self, incoming):
        #msgByte = hexStr2Byte(incoming)
        msgByte = bytearray(incoming)
        check = 0
        for i in msgByte:
            check = self.AddToCRC(i, check)
        return check

    def AddToCRC(self, b, crc):
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






class SerialLink():
    def __init__(self):
        self.BAUD              = 9600
        self.RX_POLL_PERIOD_MS = 100

        self.bcPinRx = None
        self.bcPinTx = None

        self.cbOnRxAvailable = None

        self.pigd = pigpio.pi()

    def Init(self, bcPinRx, bcPinTx, cbOnRxAvailable):
        self.bcPinRx = bcPinRx
        self.bcPinTx = bcPinTx

        self.cbOnRxAvailable = cbOnRxAvailable

        self.InitRx()
        self.InitTx()

    def InitRx(self):
        # open pin for reading serial
        self.pigd.bb_serial_read_open(self.bcPinRx, self.BAUD)

        # set up timer to check on incoming data
        evm_SetTimeout(self.OnTimeoutCheckRx, self.RX_POLL_PERIOD_MS)

    def InitTx(self):
        self.pigd.set_mode(self.bcPinTx, pigpio.OUTPUT)

        # set up timer to periodically send data
        evm_SetTimeout(self.OnTimeoutTx, 2000)




    def Send(self, buf):
        Log("Sending")
        preamble = 0x55

        # create frame
        msg = bytearray() 

        msg.append(preamble)    # preamble
        msg.append(len(buf))    # dataLength
        msg.append(0x00)        # checksum
        msg.append(0x01)        # protocolId
        #msg.append(buf)         # data
        msg.extend(buf)         # data

        crc = CRC8()
        checksum = crc.Calculate(msg)

        msg[2] = checksum

        # create serial waveform
        self.pigd.wave_clear()
        self.pigd.wave_add_serial(self.bcPinTx, self.BAUD, msg)

        serialWave = self.pigd.wave_create()

        # send serial data
        self.pigd.wave_send_once(serialWave)
        self.pigd.wave_delete(serialWave)

        # wait for TX to complete
        while self.pigd.wave_tx_busy():
            pass

        for byte in msg:
            v = float(byte) / 255. * 5.0

            Log(("%3i" % byte) + " -> " + ("%.2f" % v))
        

        Log("Sending Complete")



    def OnTimeoutCheckRx(self):
        (count, byteList) = self.pigd.bb_serial_read(self.bcPinRx)

        if count:
            print("Got " + str(count) + " bytes:")

            for byte in byteList:
                v = float(byte) / 255. * 5.0

                Log(("%3i" % byte) + " -> " + ("%.2f" % v))

        evm_SetTimeout(self.OnTimeoutCheckRx, self.RX_POLL_PERIOD_MS)

    def OnTimeoutTx(self):
        self.Send("heynow")
        evm_SetTimeout(self.OnTimeoutTx, 2000)




def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <bcPinRx> <bcPinTx>")
        sys.exit(-1)

    bcPinRx = int(sys.argv[1])
    bcPinTx = int(sys.argv[2])

    serialLink = SerialLink()
    serialLink.Init(bcPinRx, bcPinTx, None)

    Log("Waiting")
    evm_MainLoop()

#    pigd.bb_serial_read_close(bcPinRx)
#    pigd.stop()


Main()


