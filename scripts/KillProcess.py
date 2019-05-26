#!/usr/bin/python -u

import os
import subprocess
import sys

from libCore import *


def ActuallyKilled(service):
    retVal = True

    # now look and make sure it is killed
    cont = True
    secRemaining = 5
    while cont:
        time.sleep(0.5)
        running = RunInfo.ServiceIsRunning(service)

        if not running:
            cont = False

        secRemaining -= 0.5
        if not secRemaining:
            cont = False

    if running:
        retVal = False

    return retVal


def Main():
    retVal = False

    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <service>" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    service = sys.argv[1]

    if RunInfo.ServiceExists(service):
        if RunInfo.ServiceIsRunning(service):
            print("Killing %s" % service)
            try:
                pid = RunInfo.GetServicePid(service)

                subprocess.check_call(("kill " + str(pid)).split())

                if ActuallyKilled(service):
                    print("Service %s killed" % service)
                    retVal = True
                else:
                    print("Service %s was not killed after term" % service)

            except Exception as e:
                print("Service %s could not be killed: %s" % (service, e))
        else:
            print("Service %s not running" % service)
    else:
        print("Service %s does not exist" % service)

    return retVal == False


sys.exit(Main())













