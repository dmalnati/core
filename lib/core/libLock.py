import fcntl


#
# Simplify getting exclusive write locks on a file.
# Lock can't last beyond process' lifetime -- auto closed on exit.
#
# Can be used to get (shared) read or (exclusive) write locked files.
#
# wl = FileLock("file.txt")
# fd = wl.GetWriteLockedFd()
# ...
# wl.UnlockAndCloseFd()
#
# or
#
# wl = FileLock("file.txt")
# fd = wl.GetReadLockedFd()
# ...
# wl.UnlockAndCloseFd()
#
#
# https://docs.python.org/2/library/fcntl.html
# https://stackoverflow.com/questions/28470246/python-lockf-and-flock-behaviour
# https://stackoverflow.com/questions/865115/how-do-i-correctly-clean-up-a-python-object
#
class FileLock():
    def __init__(self, fName):
        self.fName   = fName
        self.fd      = None
        self.hasLock = False


    def GetWriteLockedFd(self):
        self.fd = self.OpenWrite(self.fName)

        if self.fd:
            self.hasLock = self.WriteLock(self.fd)

        if not self.hasLock:
            self.Close(self.fd)
            self.fd = None

        return self.fd


    def GetWriteAppendLockedFd(self):
        self.fd = self.OpenWriteAppend(self.fName)

        if self.fd:
            self.hasLock = self.WriteLock(self.fd)

        if not self.hasLock:
            self.Close(self.fd)
            self.fd = None

        return self.fd


    def GetReadLockedFd(self):
        self.fd = self.OpenRead(self.fName)

        if self.fd:
            self.hasLock = self.ReadLock(self.fd)

        if not self.hasLock:
            self.Close(self.fd)
            self.fd = None

        return self.fd


    def UnlockAndCloseFd(self):
        self.UnLock(self.fd)
        self.Close(self.fd)

        return True


    def OpenWrite(self, fName):
        retVal = None

        try:
            retVal = open(fName, "w")
        except:
            pass

        return retVal


    def OpenWriteAppend(self, fName):
        retVal = None

        try:
            retVal = open(fName, "a")
        except:
            pass

        return retVal


    def OpenRead(self, fName):
        retVal = None

        try:
            retVal = open(fName, "r")
        except:
            pass

        return retVal

    def Close(self, fd):
        retVal = True 

        try:
            close(fd)
        except:
            retVal = False

        return retVal


    def ReadLock(self, fd):
        retVal = True

        try:
            # shared, non-blocking.
            # the non-blocking means we get an exception if it's not
            # available right now, so we catch and return false.
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except:
            retVal = False

        return retVal


    def WriteLock(self, fd):
        retVal = True

        try:
            # exclusive, non-blocking.
            # the non-blocking means we get an exception if it's not
            # available right now, so we catch and return false.
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except:
            retVal = False

        return retVal


    def UnLock(self, fd):
        retVal = True

        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except:
            retVal = False

        return retVal





