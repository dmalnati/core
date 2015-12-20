#!/usr/bin/python

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


# Consider this:
# http://stackoverflow.com/questions/1205722/how-do-i-get-monotonic-time-durations-in-python
#
def MonitorTimerAccuracy(msTimeout):
    scope = Bunch(timeLast=time.time(), msTimeout=msTimeout)

    # let frequency be determined by command line at run time
    def OnStdin(line):
        scope.msTimeout = int(line)

    WatchStdinEndLoopOnEOF(OnStdin)

    def OnTimeout():
        timeNow = time.time()

        timeDiff   = timeNow - scope.timeLast
        timeLateUs = int((timeDiff - (scope.msTimeout / 1000.0)) * 1000000)

        scope.timeLast = timeNow

        print("timeDiff  : " + str(timeDiff))
        print("timeLateUs: " + str(timeLateUs))

        evm_SetTimeout(OnTimeout, scope.msTimeout)

    OnTimeout()
        

def Main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <msTimeout>")
        sys.exit(-1)

    msTimeout = sys.argv[1]

    MonitorTimerAccuracy(int(msTimeout))

    evm_MainLoop()


Main()


