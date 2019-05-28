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


def GetWSKillType(service):
    proc = ProcessDetails().Get(service)

    killCmd = "KILL"
    if "kill" in proc:
        killCmd = proc["kill"]

    return killCmd

def OkToKill(service):
    retVal = True

    killCmd = GetWSKillType(service)

    # handle special "SHUTDOWN" command, means don't kill ever
    if killCmd == "SHUTDOWN":
        retVal = False

    return retVal

def WSKill(service):
    killCmd = GetWSKillType(service)

    try:
        subprocess.check_output(("WSReq.py %s %s " % (service, killCmd)).split())
    except:
        pass

def Kill(pid):
    subprocess.check_call(("kill " + str(pid)).split())


def Main():
    retVal = False

    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <service>" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    service = sys.argv[1]

    if RunInfo.ServiceExists(service):
        if RunInfo.ServiceIsRunning(service):
            Log("Killing %s" % service)
            try:
                pid = RunInfo.GetServicePid(service)

                WSKill(service)

                if ActuallyKilled(service):
                    Log("Service %s killed" % service)
                    retVal = True
                else:
                    Log("Service %s was not killed via WS" % service)
                    if OkToKill(service):
                        Log("Resorting to actual kill command")

                        Kill(pid)

                        if ActuallyKilled(service):
                            Log("Service %s killed" % service)
                            retVal = True
                        else:
                            Log("Service %s was not killed after term" %
                                  service)
                    else:
                        Log("Service %s ineligible for kill command, quitting" %
                            service)
            except Exception as e:
                Log("Service %s could not be killed: %s" % (service, e))
        else:
            Log("Service %s not running" % service)
    else:
        Log("Service %s does not exist" % service)

    return retVal == False


sys.exit(Main())













