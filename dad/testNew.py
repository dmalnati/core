#!/usr/bin/python

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.app import *
from myLib.motor import *


class MyApp(WebApplicationBase):
    def Start(self, bcPin):
        Log("Starting")
        mm = MotorManager()
        self.sc = mm.GetServoControl(bcPin)

    def OnKeyboardInput(self, line):
        Log("MyApp:OnKeyboardInput: " + line)
        self.sc.MoveTo(line)

    def OnInternetGet(self, name):
        Log("MyApp:OnInternetGet: " + name)
        return "You asked for " + name

    def OnInternetSet(self, name, value):
        Log("MyApp:OnInternetSet: " + name + " = " + str(value))
        self.sc.MoveTo(value)


def Main():
    if len(sys.argv) != 2:
        Log("Usage: " + sys.argv[0] + " <bcPin>")
        sys.exit(-1)

    bcPin = sys.argv[1]

    MyApp().Start(bcPin)


Main()

