#!/usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *


class Handler(WSBridgeLoggerIface, WSBridge):
    def __init__(self, urlFirst, urlSecond):
        WSBridgeLoggerIface.__init__(self)
        WSBridge.__init__(self, urlFirst, urlSecond)

def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <urlFirst> <urlSecond>")
        sys.exit(-1)

    urlFirst  = sys.argv[1]
    urlSecond = sys.argv[2]

    b = Handler(urlFirst, urlSecond)
    Log("Bridge Starting: (" + urlFirst + ", " + urlSecond + ")")
    b.Start()

    evm_MainLoop()


Main()
