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
    logFileName += service + "_"
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

    # Change to standard directory
    #os.chdir(core + "/runtime/logs")

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
        #print("pre-fork")
        pid = os.fork()

        # get rid of the parent
        if pid > 0:
            #print("parent-fork")
            sys.exit(0)

        # child continues
        #print("child-fork")
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # actually run it now that forking over
        ActuallyRun(service, cmd)

        # try:
        #     print("pre-2nd-fork")
        #     pid = os.fork()

        #     if pid > 0:
        #         print("child-as-parent-fork")
        #         while True:
        #             sys.exit(0)

        #     print("child-of-child-fork")
        #     os.chdir("/")
        #     os.setsid()
        #     os.umask(0)


        # except Exception as e:
        #     #print("exceptInner: %s" % e)
        #     pass

    except Exception as e:
        #print("exceptOuter: %s" % e)
        pass

    return True


def Run(service):
    retVal = False

    cfgReader = ConfigReader()
    cfg = cfgReader.ReadConfig("ProcessDetails.master.json")

    for processDetail in cfg["processDetailsList"]:
        if service == processDetail["name"]:
            cmd = processDetail["cmd"]

            print("Running %s - %s" % (service, cmd))

            ForkDaemon(service, cmd)

            retVal = True
            break

    if not retVal:
        print("Service %s not found" % service)

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


