import time
import os

from libUtl import *
from libCoreDir import *
from libLock import *



#
# Reads and Maintains a file with information about the state of the server.
#
# File is 2 lines:
# <state>
# <pidOfLockHolder>
#
# If no lock held, then the 2nd line is who last wrote the state.
#
# If there is no state file, state is defaulted to CLOSED.
#
# The states are:
# STARTING
# STARTED
# CLOSING
# CLOSED
#
class ServerState():
    def __init__(self):
        self.stateFile = CorePath("/runtime/working/ServerState.txt")
        self.fl        = FileLock(self.stateFile)
        self.fd        = None


    def GetStateLock(self):
        retVal = False

        self.fd = self.fl.GetWriteAppendLockedFd()

        if self.fd:
            retVal = True

        return retVal


    def ReleaseStateLock(self):
        return self.fl.UnlockAndCloseFd()


    def GetState(self):
        retVal = "CLOSED"

        fd = None

        try:
            fd = open(self.stateFile, "r")
        except:
            pass


        if fd:
            state = fd.readline().strip()

            try:
                close(fd)
            except:
                pass
            
            if self.IsValidState(state):
                retVal = state

        return retVal


    def GetTimeOfLastChange(self):
        retVal = None

        try:
            unixTime = os.path.getmtime(self.stateFile)

            retVal = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))
        except:
            pass

        return retVal

    def GetDurationOfCurrentStateSecs(self):
        retVal = 0

        timeThen = self.GetTimeOfLastChange()

        if timeThen:
            timeNow = DateTimeNow()

            retVal = DateTimeStrDiffSec(timeNow, timeThen)

        return retVal

    def GetDurationOfCurrentStateFormatted(self):
        secsDiff = self.GetDurationOfCurrentStateSecs()

        return SecsToDuration(secsDiff)


    def SetState(self, state):
        retVal = False

        if self.IsValidState(state):
            if self.fd:
                retVal = True

                pid = os.getpid()

                self.fd.truncate(0)
                self.fd.write(state + "\n" + str(pid) + "\n")
                self.fd.flush()

        return retVal


    def IsValidState(self, state):
        retVal = False

        if state == "STARTING" or \
           state == "STARTED"  or \
           state == "CLOSING"  or \
           state == "CLOSED":
            retVal = True

        return retVal


