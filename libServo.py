import math
import time

import RPi.GPIO as GPIO


#
# Expects to be asked to move the servo anywhere between 0-100% range
# inclusive.
#
# Assumes pwm frequency of 50Hz.
#
# Caller must take care to call GPIO setup/cleanup as appropriate.  EG:
# - GPIO.setmode(GPIO.BOARD)
# - GPIO.SETUP(7, GPIO.OUT)
# - ...
# - GPIO.cleanup()
#
class ServoControlDiscrete():
    def __init__(self,
                 pin,
                 pwLow=0.5,
                 pwHigh=2.5,
                 hertz=50,
                 degRange=180,
                 degPerSec=60):
        self.pin       = int(pin)
        self.pwLow     = float(pwLow)
        self.pwHigh    = float(pwHigh)
        self.hertz     = int(hertz)
        self.degRange  = float(degRange)
        self.degPerSec = float(degPerSec)
        self.p         = GPIO.PWM(self.pin, self.hertz)

        self.degLast = None

        self.Start()

    def __del__(self):
        self.Stop()

    def Start(self):
        self.p.start(self.hertz)

    def Stop(self):
        self.p.stop()

    def MoveTo(self, pct):
        pct = float(pct)

        if pct < 0:
            pct = 0.0
        elif pct > 100:
            pct = 100

        # determine pulse width
        pw = self.pwLow + ((self.pwHigh - self.pwLow) * (pct / 100.0))

        # determine the "percent of pulse with at x hertz" as required by
        # the GPIO functions.
        # EG if 50 hertz, that is a 20ms interval.  We don't care about that
        # very much per-se.
        # What we care about is that we want to apply a 'high' value for
        # a given width (time).  We might think that time falls within the
        # range of pwLow-pwHigh, and it does, except the GPIO functions want
        # that expressed as a percent of the 20ms period at 50 hertz.
        # In the end, if 2ms pulse is needed, that's 10% of the 20ms period
        # which 50 hertz operates at.
        pctOfHertzPeriod = float(pw) / (1000.0 / self.hertz) * 100.0

        # determine the degree position
        degNew = (pct / 100.0) * self.degRange

        # determine the duration of time to apply the pwm signal based on
        # the time taken to get to new position based on old position
        # if known.
        # default to time to move the whole range (worst case)
        pwmSecs = self.degRange / self.degPerSec
        if self.degLast != None:
            pwmSecs = math.fabs(degNew - self.degLast) / self.degPerSec
        self.degLast = degNew

        # Move
        self.p.ChangeDutyCycle(pctOfHertzPeriod)
        time.sleep(pwmSecs)

        









