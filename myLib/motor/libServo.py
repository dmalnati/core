import math
import time

import pigpio


class ServoControl():
    def __init__(self,
                 pigd,
                 bcPin,
                 msPulseLow=500,
                 msPulseHigh=2500,
                 degRange=180):
        self.pigd        = pigd
        self.bcPin       = int(bcPin)
        self.msPulseLow  = float(msPulseLow)
        self.msPulseHigh = float(msPulseHigh)
        self.degRange    = float(degRange)

        self.degLast = None


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

        # apply indefinitely
        self.pigd.set_servo_pulsewidth(self.bcPin, msPulse)


    def Stop(self):
        self.pigd.stop()


