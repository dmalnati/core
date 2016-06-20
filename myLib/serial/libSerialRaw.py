#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


class SerialRaw():
    def __init__(self,
                 bcPinRx=None,
                 bcPinTx=None,
                 baud=9600,
                 pollPeriodRx=50):
        self.BAUD              = baud
        self.RX_POLL_PERIOD_MS = pollPeriodRx

        self.bcPinRx = bcPinRx
        self.bcPinTx = bcPinTx

        self.cbOnRxAvailable = None

        self.pigd = pigpio.pi()

        if self.bcPinRx:
            self.InitRx()

        if self.bcPinTx:
            self.InitTx()

    def Stop(self):
        if self.bcPinRx:
            self.pigd.bb_serial_read_close(self.bcPinRx)

        self.pigd.stop()

    def SetCbOnRxAvailable(self, cbOnRxAvailable):
        self.cbOnRxAvailable = cbOnRxAvailable

    def InitRx(self):
        if self.bcPinRx:
            # open pin for reading serial
            pigpio.exceptions = False
            self.pigd.bb_serial_read_close(self.bcPinRx)
            pigpio.exceptions = True
            self.pigd.bb_serial_read_open(self.bcPinRx, self.BAUD)

            # set up timer to check on incoming data
            evm_SetTimeout(self.OnTimeoutCheckRx, self.RX_POLL_PERIOD_MS)

    def InitTx(self):
        if self.bcPinTx:
            pigpio.exceptions = False
            self.pigd.set_mode(self.bcPinTx, pigpio.OUTPUT)
            pigpio.exceptions = True


    def Send(self, buf):
        if self.bcPinTx:
            # Create bytearray
            msg = bytearray() 

            # Add data
            msg.extend(buf)

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

    def OnTimeoutCheckRx(self):
        (count, byteList) = self.pigd.bb_serial_read(self.bcPinRx)

        if self.cbOnRxAvailable:
            self.cbOnRxAvailable(byteList)

        evm_SetTimeout(self.OnTimeoutCheckRx, self.RX_POLL_PERIOD_MS)
