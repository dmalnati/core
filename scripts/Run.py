#!/usr/bin/python -u


import atexit
import ctypes
import datetime
import os
import sys
import time
import shutil
import subprocess

from libCore import * 


def ActuallyRun(service, cmd):
    # Determine log file name
    core = os.environ["CORE"]
    logFileName  = core + "/runtime/logs/"
    logFileName += service + "."
    logFileName += datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    logFileName += ".txt"

    # Create and open log file
    fdOut = open(logFileName, "w")

    # make sure parent takes out child when it goes
    libc = ctypes.CDLL("libc.so.6")
    def set_pdeathsig(sig = signal.SIGTERM):
        def callable():
            return libc.prctl(1, sig)
        return callable

    # Give process an input file descriptor which will never read active
    fdRead, fdWrite = os.pipe()

    # Invoke
    proc = subprocess.Popen(cmd.split(),
                            stdin=fdRead,
                            stdout=fdOut,
                            stderr=subprocess.STDOUT,
                            preexec_fn = set_pdeathsig(signal.SIGTERM))

    # Cause parent to wait around so it can be seen in process list
    proc.wait()


def ForkDaemon(service, cmd):
    try:
        pid = os.fork()

        # get rid of the parent
        if pid > 0:
            sys.exit(0)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        # actually run it now that forking over
        ActuallyRun(service, cmd)

    except Exception as e:
        pass

    return True


def Run(service):
    retVal = False

    cfgReader = ConfigReader()
    cfg = cfgReader.ReadConfig("ProcessDetails.master.json")

    for processDetail in cfg["processDetailsList"]:
        if service == processDetail["name"]:
            cmd = processDetail["cmd"]
            
            # Set up run environment for this service
            os.environ["CORE_SERVICE_NAME"] = service

            Log("Running %s - %s" % (service, cmd))

            ForkDaemon(service, cmd)

            retVal = True
            break

    if not retVal:
        Log("Service %s not found" % service)

    return retVal

def Main():
    retVal = True

    if len(sys.argv) > 3 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <service> " % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    service = sys.argv[1]

    retVal = Run(service)

    return retVal == False

sys.exit(Main())


