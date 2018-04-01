import time

import pigpio



#
# https://www.mouser.com/ds/2/813/hx711_english-1022875.pdf
#
# PD_SCK Pulses   Input channel   Gain
# 25              A               128
# 27              A                64 
# 26              B                32
#
# (yes the pulse counts don't seem in order, but this is what the spec says)
#

class HX711:
    def __init__(self, bcPinClk, bcPinSerial):
        self.pig         = pigpio.pi()
        self.bcPinClk    = bcPinClk
        self.bcPinSerial = bcPinSerial

        self.pig.set_mode(self.bcPinClk,    pigpio.OUTPUT)
        self.pig.set_mode(self.bcPinSerial, pigpio.INPUT)

        # initial state of clock pin is LOW
        self.pig.write(self.bcPinClk, 0)

        # set up gain
        self.pulseCount = 25;   # default to gain 128

        # deal with first measurement issue
        self.firstMeasurement = 1

        # support calibration
        self.useCalibration = 0

        # support throwing away absurdly high values
        self.discardAbove         = 0
        self.discardAboveMaxTries = 100


    def __del__(self):
        self.pig.stop()

    def SetGain(self, gain):
        if gain == 32:
            self.pulseCount = 26
        if gain == 64:
            self.pulseCount = 27
        if gain == 128:
            self.pulseCount = 25

    def SetCalibration(self, subtract, divide):
        self.useCalibration = 1
        self.subtract = subtract
        self.divide   = divide

    def SetDiscardAbove(self, discardAbove, maxTries = 100):
        self.discardAbove         = discardAbove
        self.discardAboveMaxTries = maxTries

    def GetMeasurement(self):
        if self.firstMeasurement:
            # throw away first measurements which are wrong initially
            throwAwayRemaining = 5
            while throwAwayRemaining:
                self.GetMeasurementInternal()
                throwAwayRemaining -= 1

            self.firstMeasurement = 0

        retVal = self.GetMeasurementInternal()

        if self.discardAbove:
            triesRemaining = self.discardAboveMaxTries

            while retVal > self.discardAbove and triesRemaining:
                retVal = self.GetMeasurementInternal()

                triesRemaining = triesRemaining - 1

        return retVal

    def GetMeasurementInternal(self):
        retVal = 0

        # wait for "measurement ready" signal of serial pin going LOW
        while self.pig.read(self.bcPinSerial):
            pass

        # extract the 24 bits of data
        bitCount = 24
        while bitCount:
            self.pig.gpio_trigger(self.bcPinClk, 10, 1)

            bitVal = self.pig.read(self.bcPinSerial)
            retVal = (retVal << 1) | bitVal

            bitCount = bitCount - 1


        # send the 25th and beyond clock pulse to complete operation
        # this is based on the gain configured elsewhere
        pulsesRemaining = self.pulseCount - 24

        while pulsesRemaining:
            self.pig.gpio_trigger(self.bcPinClk, 10, 1)
            pulsesRemaining -= 1;

        # use calibration if set
        if self.useCalibration:
            retVal = (retVal - self.subtract) / self.divide

        return retVal




