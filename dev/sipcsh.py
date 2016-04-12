#!/usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.simpleIPC import *


def Main():
    if len(sys.argv) != 3 and len(sys.argv) != 6:
        print("Two modes -- Serial or RFLink:")
        print("Serial: " + sys.argv[0] + " <bcPinRx> <bcPinTx>")
        print("RFLink: " +
              sys.argv[0] +
              " <bcPinRx> <bcPinTx> <realm> <srcAddr> <dstAddr>")
        sys.exit(-1)

    # Parse command line
    bcPinRx = int(sys.argv[1])
    bcPinTx = int(sys.argv[2])

    # Get Manager
    mgr = None
    if len(sys.argv) == 3:
        mgr = SimpleIPCManager(bcPinRx, bcPinTx)
    else:
        realm   = int(sys.argv[3])
        srcAddr = int(sys.argv[4])
        dstAddr = int(sys.argv[5])

        mgr = SimpleIPCManager(bcPinRx, bcPinTx, realm, srcAddr, dstAddr)

    # Run interactive shell
    mgr.RunInteractiveShell()

    # Main Loop
    evm_MainLoop()


Main()


