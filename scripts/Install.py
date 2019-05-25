#!/usr/bin/python -u


import os
import sys

from shutil import copyfile

from libCore import *


def SetupDirectories():
    retVal = False

    Log("Setting up directories")

    core = os.environ["CORE"]

    directoryList = [
        core + "/archive",
        core + "/generated-cfg",
        core + "/site-specific",
        core + "/site-specific/cfg",
        core + "/runtime",
        core + "/runtime/logs",
    ]

    try:
        for directory in directoryList:
            if not os.path.exists(directory):
                os.makedirs(directory)

        retVal = True
    except:
        pass

    if retVal:
        Log("  OK")
    else:
        Log("  NOT OK")

    return retVal

def GenerateConfig():
    retVal = False

    Log("Generating Configuration")

    core = os.environ["CORE"]

    srcFile = core + "/core/cfg/WSServices.txt"
    dstFile = core + "/generated-cfg/WSServices.txt"

    Log(srcFile + " -> " + dstFile)

    try:
        copyfile(srcFile, dstFile)

        retVal = True
    except:
        pass

    if retVal:
        Log("  OK")
    else:
        Log("  NOT OK")


def Main():
    if len(sys.argv) > 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    if "CORE" in os.environ:
        retValSD = SetupDirectories()
        retValGC = GenerateConfig()

    Log("DONE")

    return (retValSD and retValGC) == False

sys.exit(Main())










