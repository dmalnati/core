import time

import pigpio


class PumpPwm:
    def __init__(self, bcPin):
        self.pig   = pigpio.pi()
        self.bcPin = bcPin

    def SetPwmPct(self, pct):
        pwmDutyCycle = int(float(pct) * 255.0 / 100.0)

        self.pig.set_PWM_dutycycle(self.bcPin, pwmDutyCycle)

    def End(self):
        self.pig.set_PWM_dutycycle(self.bcPin, 0)

        self.pig.stop()


