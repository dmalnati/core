#!/usr/bin/python -u


import os
import sys



def SetupDirectories():
    retVal = False

    print("Setting up directories")

    if "CORE" in os.environ:
        coreStr = os.environ["CORE"]

        directoryList = [
            coreStr + "/archive",
            coreStr + "/generated-cfg",
            coreStr + "/site-specific",
            coreStr + "/site-specific/cfg",
            coreStr + "/runtime",
            coreStr + "/runtime/logs",
        ]

        try:
            for directory in directoryList:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            retVal = True
        except:
            pass

    if retVal:
        print("  OK")
    else:
        print("  NOT OK")

    return retVal


def Main():
    if len(sys.argv) > 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    retValSD = SetupDirectories()

    print("DONE")

    return (retValSD) == False

sys.exit(Main())










