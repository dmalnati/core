#!/usr/bin/python3.5 -u

import os
import subprocess
import sys
import time

from libCore import *


def Main():
    retVal = False

    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <service>" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    service = sys.argv[1]

    if RunInfo.ServiceExists(service):
        # Kill off if necessary
        if RunInfo.ServiceIsRunning(service):
            try:
                subprocess.check_call(("KillProcess.py " + service).split())
                retVal = True
            except Exception as e:
                retVal = False
        else:
            retVal = True

        if retVal:
            # Now start it
            if not RunInfo.ServiceIsRunning(service):
                try:
                    subprocess.check_call(("StartProcess.py " + service).split())
                    retVal &= True
                except Exception as e:
                    retVal = False
                    pass
            else:
                Log("Service %s running when it shouldn't be, quitting" % service)
                retVal = False
    else:
        Log("Service %s does not exist" % service)

    return retVal == False


sys.exit(Main())













