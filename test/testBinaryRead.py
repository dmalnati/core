#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


def OnBinaryData(byteList):
    print("got " + str(len(byteList)) + " bytes")

def Main():

    WatchStdinEndLoopOnEOF(OnBinaryData, binary=True)

    evm_MainLoop()


Main()


