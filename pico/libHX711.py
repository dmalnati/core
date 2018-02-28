import time

import pigpio


class HX711:
    def __init__(self, bcPinClk, bcPinSerial):
        self.pig         = pigpio.pi()
        self.bcPinClk    = bcPinClk
        self.bcPinSerial = bcPinSerial

        self.pig.set_mode(self.bcPinClk,    pigpio.OUTPUT)
        self.pig.set_mode(self.bcPinSerial, pigpio.INPUT)

        # initial state of clock pin is LOW
        self.pig.write(self.bcPinClk, 0)


    def __del__(self):
        self.pig.stop()


    def GetMeasurement(self):
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

        # send the 25th clock pulse to complete operation
        self.pig.gpio_trigger(self.bcPinClk, 10, 1)

        return retVal




