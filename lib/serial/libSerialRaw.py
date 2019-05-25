#!/usr/bin/python

import sys
import os
import time

import pigpio

from libEvm import *


class SerialRaw():
    def __init__(self,
                 bcPinRx=None,
                 bcPinTx=None,
                 baud=9600,
                 pollPeriodRx=1):
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

    def EnableGlitchFilter(self):
        # Sets a glitch filter on a GPIO. 
        # Level changes on the GPIO are not reported unless the level has been
        # stable for at least steady microseconds.
        # The level is then reported.
        # Level changes of less than steady microseconds are ignored. 
        self.pigd.set_glitch_filter(self.bcPinRx, 10)

    def InitRx(self):
        if self.bcPinRx:
            # open pin for reading serial
            pigpio.exceptions = False
            self.pigd.bb_serial_read_close(self.bcPinRx)
            pigpio.exceptions = True
            self.pigd.bb_serial_read_open(self.bcPinRx, self.BAUD)

            # Set up glitch filter
            self.EnableGlitchFilter()

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

        if count and self.cbOnRxAvailable:
            self.cbOnRxAvailable(byteList)

        evm_SetTimeout(self.OnTimeoutCheckRx, self.RX_POLL_PERIOD_MS)

