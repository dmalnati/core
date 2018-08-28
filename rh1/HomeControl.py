#!/usr/bin/python -u

import os
import sys
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.app import *


class MyApp(WebApplicationBase):
    def Start(self):
        self.service__pin = {
            # Air Conditioners
            "AC1" : 20,
            "AC2" : 21,
            # Power Strip
            "PS1" : 2,
            "PS2" : 3,
            "PS3" : 4,
            "PS4" : 17,
            "PS5" : 27,
            "PS6" : 22,
        }

        self.pig = pigpio.pi()

        for service in sorted(self.service__pin.keys()):
            pin = self.service__pin[service]
            Log("Setting " + service + "(pin " + str(pin) + ") to LOW")
            self.pig.set_mode(pin, pigpio.OUTPUT)
            self.pig.write(pin, 0)

        Log("Starting")

    def OnKeyboardInput(self, line):
        Log("MyApp:OnKeyboardInput: " + line)

    def OnInternetGet(self, name):
        retVal = 0

        #Log("MyApp:OnInternetGet: " + name)

        if name in self.service__pin:
            pin = self.service__pin[name]
            retVal = self.pig.read(pin)

        #Log("  returning: " + str(retVal))

        return str(retVal)

    def OnInternetSet(self, name, value):
        Log("MyApp:OnInternetSet: " + name + " = " + str(value))

        if name in self.service__pin:
            pin = self.service__pin[name]
            self.pig.write(pin, int(value))


def Main():
    LogIncludeDate(True)

    if len(sys.argv) != 1 and len(sys.argv) != 2:
        Log("Usage: " + sys.argv[0])
        sys.exit(-1)

    if len(sys.argv) == 2:
        webRoot = sys.argv[1]
        MyApp(webRoot=webRoot, enableKeyboardInput=False).Start()
    else: 
        MyApp(enableKeyboardInput=False).Start()


Main()

