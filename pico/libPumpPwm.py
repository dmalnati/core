import time

import pigpio


class PumpPwm:
    def __init__(self, bcPin):
        self.pig     = pigpio.pi()
        self.bcPin   = bcPin
        self.pctLast = 0

    def SetPwmPct(self, pct):
        pwmDutyCycle = int(float(pct) * 255.0 / 100.0)

        # take time to change pct to ease dramatic current changes
        pwmDutyCycleLast = int(float(self.pctLast) * 255.0 / 100.0)

        pwmDutyCycleDiff = pwmDutyCycle - pwmDutyCycleLast

        incr = 0
        if pwmDutyCycleDiff < 0:
            incr = -1
        else:
            incr = 1

        pwmDutyCycleTmp = pwmDutyCycleLast

        while pwmDutyCycleTmp != pwmDutyCycle:
            self.pig.set_PWM_dutycycle(self.bcPin, pwmDutyCycleTmp)
            time.sleep(0.002)

            pwmDutyCycleTmp += incr

        # remember for next time
        self.pctLast = pct

    def End(self):
        self.pig.set_PWM_dutycycle(self.bcPin, 0)

        self.pig.stop()


