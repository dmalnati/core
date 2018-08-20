#!/usr/bin/python

import os
import sys
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.app import *


class MyApp(WebApplicationBase):
    def Start(self):
        self.PIN_AC1 = 20
        self.PIN_AC2 = 21

        self.pig = pigpio.pi()

        self.pig.set_mode(self.PIN_AC1, pigpio.OUTPUT)
        self.pig.set_mode(self.PIN_AC2, pigpio.OUTPUT)

        self.pig.write(self.PIN_AC1, 0)
        self.pig.write(self.PIN_AC2, 0)

        self.AC1 = 0
        self.AC2 = 0

        Log("Starting")

    def OnKeyboardInput(self, line):
        Log("MyApp:OnKeyboardInput: " + line)

    def OnInternetGet(self, name):
        retVal = 0

        Log("MyApp:OnInternetGet: " + name)

        if name == "AC1":
            retVal = self.AC1
        elif name == "AC2":
            retVal = self.AC2

        Log("  returning: " + str(retVal))

        return str(retVal)

    def OnInternetSet(self, name, value):
        Log("MyApp:OnInternetSet: " + name + " = " + str(value))

        if name == "AC1":
            self.AC1 = value
            self.pig.write(self.PIN_AC1, int(value))
        elif name == "AC2":
            self.AC2 = value
            self.pig.write(self.PIN_AC2, int(value))


def Main():
    if len(sys.argv) != 1:
        Log("Usage: " + sys.argv[0])
        sys.exit(-1)

    MyApp().Start()


Main()

