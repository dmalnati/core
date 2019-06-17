#!/usr/bin/python3.5 -u

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
        time.sleep(0.1)
        running = RunInfo.ServiceIsRunning(service)

        if not running:
            cont = False

        secRemaining -= 0.5
        if not secRemaining:
            cont = False

    if running:
        retVal = False

    return retVal



def GetKillTechniqueList(service):
    proc = ProcessDetails().Get(service)

    killTechniqueList = ["KILL", "SIGNAL"]

    if "kill" in proc:
        killTechniqueList = proc["kill"]

    return killTechniqueList



def WSKill(service, killCmd):
    try:
        subprocess.check_output(("WSReq.py %s %s" % (service, killCmd)).split())
    except:
        pass


def SigKill(pid):
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

            killTechniqueList = GetKillTechniqueList(service)

            if len(killTechniqueList):
                for killTechnique in killTechniqueList:
                    killAttempted = True

                    if killTechnique == "SHUTDOWN" or killTechnique == "KILL":
                        Log("  Attempting %s" % killTechnique)

                        WSKill(service, killTechnique)
                    elif killTechnique == "SIGNAL":
                        Log("  Attempting %s" % killTechnique)

                        pid = RunInfo.GetServicePid(service)
                        SigKill(pid)
                    else:
                        Log("  Kill mode %s not valid, skipping" % killTechnique)
                        killAttempted = False

                    if killAttempted:
                        if ActuallyKilled(service):
                            Log("Service %s killed" % service)
                            retVal = True
                            break
                        else:
                            Log("  Service %s was not killed by %s" % (service, killTechnique))

                if retVal != True:
                    Log("Service %s not killed, all attempts failed" % service)
            else:
                Log("Service %s configured to not be killed" % service)
                retVal = True
        else:
            Log("Service %s not running" % service)
    else:
        Log("Service %s does not exist" % service)

    return retVal == False


sys.exit(Main())













