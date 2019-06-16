#!/usr/bin/python -u


import getpass
import os
import sys

from libCore import *

    
    



# https://www.brendanlong.com/systemd-user-services-are-amazing.html
def UninstallService():
    service             = "core_systemd.service"
    user                = getpass.getuser()
    dirSystemd          = user + "/.config/systemd/user"
    serviceFileFullPath = dirSystemd + '/' + service

    SafeMakeDir(dirSystemd)

    ok = True

    # this disables bootup running of the service despite the user not being logged in
    if ok:
        try:
            RunCommand("sudo loginctl disable-linger %s" % user)
        except Exception as e:
            ok = False
            Log("Could not disable boot start for user %s: %s" % (user, e))

    # this disables the user service described in the service file
    if ok:
        try:
            RunCommand("systemctl --user disable %s" % service)
        except Exception as e:
            ok = False
            Log("Could not disable service: %s" % e)

    SafeRemoveFileIfExists(serviceFileFullPath)

    return ok




def Main():
    retVal = True

    if len(sys.argv) > 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    if "CORE" in os.environ:
        forceFlag = False
        if len(sys.argv) == 2 and sys.argv[1] == "--force":
            forceFlag = True

        ss = ServerState()

        # check if state lock acquired, allow force
        movePastLock = True
        if not ss.GetStateLock():
            movePastLock = False

            if forceFlag:
                movePastLock = True
                Log("Force installing despite not acquiring lock")

        if movePastLock:
            state = ss.GetState()

            # check if state correct, allow force
            movePastState = True
            if not state == "CLOSED":
                movePastState = False

                if forceFlag:
                    movePastState = True
                    Log("Force installing despite state %s "
                        "not being CLOSED" % state)

            if movePastState:
                retVal = UninstallService()

                Log("DONE")
            else:
                Log("State %s, needs to be CLOSED, quitting" % state)
                retVal = False

            ss.ReleaseStateLock()
        else:
            Log("State locked, operation in progress elsewhere, quitting")
            retVal = False


    return retVal == False

sys.exit(Main())










