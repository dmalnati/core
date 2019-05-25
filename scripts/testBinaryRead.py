#!/usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from lib.utl import *


def OnBinaryData(byteList):
    print("got " + str(len(byteList)) + " bytes")

def Main():

    WatchStdinEndLoopOnEOF(OnBinaryData, binary=True)

    evm_MainLoop()


Main()


