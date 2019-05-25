
import pigpio

from libServo import *


class MotorManager():
    def __init__(self, *args, **kwargs):
        self.pigd = pigpio.pi()
 
    def GetServoControl(self, bcPin):
        return ServoControl(self.pigd, bcPin)



