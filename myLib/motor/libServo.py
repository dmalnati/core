import math
import time

import pigpio

from ..utl import *

class ServoControl():
    def __init__(self,
                 pigd,
                 bcPin,
                 msPulseLow=500,
                 msPulseHigh=2500,
                 degRange=180,
                 pwmDurationBeforeOff=1500):
        self.pigd        = pigd
        self.bcPin       = int(bcPin)
        self.msPulseLow  = float(msPulseLow)
        self.msPulseHigh = float(msPulseHigh)
        self.degRange    = float(degRange)

        self.degLast = None

        self.pwmDurationBeforeOff = pwmDurationBeforeOff
        self.timerHandle = None


    # deg from -(.5 * degRange) to (.5 * degRange)
    # when negative, turn servo left.  The lower the number, the more left.
    # when positive, turn servo right. The higher the number, the more right.
    # when zero, align to center
    def MoveTo(self, deg):
        deg = float(deg)

        halfDegRange = (self.degRange / 2.0)

        # constrain range
        if deg < -halfDegRange:
            deg = -halfDegRange
        elif deg > halfDegRange:
            deg = halfDegRange

        # map to ms pulse duration
        degMappedToPositiveRange = halfDegRange + deg
        degAsPctOfPositiveRange  = degMappedToPositiveRange / self.degRange

        msPulse = \
            self.msPulseLow + \
            ((self.msPulseHigh - self.msPulseLow) * degAsPctOfPositiveRange)

        # apply
        self.pigd.set_servo_pulsewidth(self.bcPin, msPulse)

        # Start timer to end pwm once enough time has gone by that the
        # servo should be in place.
        self.StartTimer()

    def TurnOffPWM(self):
        self.pigd.set_servo_pulsewidth(self.bcPin, 0)

    def StartTimer(self):
        self.CancelTimer()
        self.timerHandle = evm_SetTimeout(self.OnTimeout,
                                          self.pwmDurationBeforeOff)

    def CancelTimer(self):
        if self.timerHandle != None:
            evm_CancelTimeout(self.timerHandle)
            self.timerHandle = None

    def OnTimeout(self):
        self.timerHandle = None
        self.TurnOffPWM()

    def Stop(self):
        self.CancelTimer()
        self.TurnOffPWM()
        self.pigd.stop()



