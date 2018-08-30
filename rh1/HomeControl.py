#!/usr/bin/python -u

import os
import sys
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.app import *



class Pin():
    def __init__(self, highLowType, bcPin):
        self.highLowType = highLowType
        self.bcPin       = bcPin

    def GetHighLow(self, logicalValue):
        retVal = logicalValue

        if self.highLowType == "LOW":
            if logicalValue:
                retVal = 0
            else:
                retVal = 1

        return retVal

    def GetPin(self):
        return self.bcPin
        

class MyApp(WebApplicationBase):
    def Start(self):
        self.service__pin = {
            # Air Conditioners
            "AC1" : Pin("HIGH", 20),
            "AC2" : Pin("HIGH", 21),
            # Power Strip
            "PS1" : Pin("LOW", 2),
            "PS2" : Pin("LOW", 3),
            "PS3" : Pin("LOW", 17),
            "PS4" : Pin("LOW", 27),
            "PS5" : Pin("LOW", 22),
            "PS6" : Pin("LOW", 26),
        }

        self.pig = pigpio.pi()

        for service in sorted(self.service__pin.keys()):
            pin = self.service__pin[service]
            Log("Setting " + service + "(pin " + str(pin.GetPin()) + ") to LOW")
            self.pig.set_mode(pin.GetPin(), pigpio.OUTPUT)
            self.pig.write(pin.GetPin(), pin.GetHighLow(0))

        Log("Starting")

    def OnKeyboardInput(self, line):
        Log("MyApp:OnKeyboardInput: " + line)

    def OnInternetGet(self, name):
        retVal = 0

        if name in self.service__pin:
            pin = self.service__pin[name]
            retVal = pin.GetHighLow(self.pig.read(pin.GetPin()))

        #Log("MyApp:OnInternetGet: " + name + " => " + str(retVal))

        return str(retVal)

    def OnInternetSet(self, name, value):
        if name in self.service__pin:
            pin = self.service__pin[name]
            self.pig.write(pin.GetPin(), pin.GetHighLow(int(value)))

        Log("MyApp:OnInternetSet: " + name + " <= " + str(value))


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

