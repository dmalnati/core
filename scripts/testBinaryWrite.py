#!/usr/bin/python

import sys
import os

from libCore import *


def OnStdin(line):
    if line != "":
        linePartList = line.split(" ")

        count = int(linePartList[0])
        char  = linePartList[1][:1]

        for i in range(count):
            sys.stdout.write(char)

        sys.stdout.flush()

def Main():
    WatchStdinEndLoopOnEOF(OnStdin)

    evm_MainLoop()


Main()


