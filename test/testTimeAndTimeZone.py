#!/usr/bin/python -u

import sys
import os

from libCore import *


class App:
    def __init__(self):
        self.tatz          = TimeAndTimeZone()
        self.formatStrFull = "%Y-%m-%d %H:%M:%S %Z%z"
        
    def OnStdIn(self, line):
        linePartList = line.split()

        cmd = linePartList[0]

        if cmd == "set":
            timeStr   = linePartList[1]
            formatStr = linePartList[2]
            timeZone  = linePartList[2]

            self.tatz.SetTime(timeStr, formatStr, timeZone)

        elif cmd == "get":
            timeZone = linePartList[1]

            print(self.tatz.GetTimeNativeInTimeZone(timeZone).strftime(self.formatStrFull))
        elif cmd == "test":
            self.DoTest()

    def DoTest(self):
        timeStr   = "2019-06-04 13:54"
        formatStr = "%Y-%m-%d %H:%M"
        timeZone  = "UTC"
        timeZone  = "US/Pacific"
        timeZone  = "US/Eastern"
        timeZone  = "EST"

        # beware that the above can be an explicit daylight savings vs not (EST vs EDT).
        # alternatively US/Eastern seems to be whatever it is right now.

        print("SetTime(%s, %s, %s)" % (timeStr, formatStr, timeZone))

        self.tatz.SetTime(timeStr, formatStr, timeZone)

        timeNative = self.tatz.GetTimeNative()

        print("post-SetTime: \"%s\"" % timeNative.strftime(self.formatStrFull))

        timeNativeUtc = self.tatz.GetTimeNativeInTimeZone("UTC")
        print("UTC: \"%s\"" % timeNativeUtc.strftime(self.formatStrFull))

        timeNativeEST = self.tatz.GetTimeNativeInTimeZone("EST")
        print("EST: \"%s\"" % timeNativeEST.strftime(self.formatStrFull))

        timeNativePST = self.tatz.GetTimeNativeInTimeZone("US/Pacific")
        print("PST: \"%s\"" % timeNativePST.strftime(self.formatStrFull))


    def Run(self):
        self.DoTest()
        WatchStdinLinesEndLoopOnEOF(self.OnStdIn)
        evm_MainLoop()


def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())














