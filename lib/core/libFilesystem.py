import os
import sys
import shutil
import glob

import subprocess

from distutils import dir_util
from shutil import copyfile, move

from libUtl import *


def Glob(pattern):
    retVal = glob.glob(pattern)

    return retVal

def FileFullPath(file):
    return os.path.abspath(file)

def FileExists(file):
    return os.path.isfile(file)

def GetFileModificationTime(file):
    unixTime = 0

    try:
        unixTime = os.path.getmtime(file)
    except:
        pass

    return unixTime

def GetFileModificationTimeFormatted(file):
    unixTime = GetFileModificationTime(file)

    retVal = unixTime

    try:
        retVal = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))
    except:
        pass

    return retVal
    
def GetFileSize(file):
    size = 0
    
    try:
        size = os.path.getsize(file)
    except:
        pass
    
    return size

def SafeCopyFileIfExists(srcFile, dstFile):
    retVal = True

    if FileExists(srcFile):
        try:
            copyfile(srcFile, dstFile)
        except:
            retVal = False

    return retVal

def DirectoryPart(file):
    return os.path.dirname(file)

def FilePart(file):
    return os.path.basename(file)

def SafeMoveFileIfExists(srcFile, dstFile):
    retVal = True

    if FileExists(srcFile):
        SafeMakeDir(DirectoryPart(dstFile))

        try:
            move(srcFile, dstFile)
        except:
            retVal = False

    return retVal
    

def RemoveDir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)

def SafeMakeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def SafeRemoveFileIfExists(file):
    if FileExists(file):
        os.unlink(file)

def MakeTmpDir():
    directory = "/tmp/" + str(os.getpid())
    SafeMakeDir(directory)
    return directory

def DeleteFilesInDir(directory):
    retVal = True

    for f in os.listdir(directory):
        try:
            fFullPath = directory + "/" + f
            SafeRemoveFileIfExists(fFullPath)
        except:
            retVal = False

    return retVal


def SafeRecursiveDirectoryCopy(srcDir, dstDir):
    dir_util.copy_tree(srcDir, dstDir)


def CopyFiles(srcDir, dstDir, verbose = False):
    retVal = True

    if os.path.isdir(srcDir):
        for f in os.listdir(srcDir):
            if f[0] != '.':
                fFullPath = srcDir + "/" + f

                if FileExists(fFullPath):
                    srcFile = fFullPath
                    dstFile = dstDir + "/" + f

                    if SafeCopyFileIfExists(srcFile, dstFile):
                        if verbose:
                            Log(srcFile + " -> ")
                            Log(dstFile)
                            Log("")
                    else:
                        retVal = False

    return retVal


#
# df

# Filesystem     1K-blocks    Used Available Use% Mounted on
# /dev/root       30551492 5428844  23831792  19% /
# devtmpfs          476224       0    476224   0% /dev
# tmpfs              96168    4652     91516   5% /run
# tmpfs               5120       0      5120   0% /run/lock
# tmpfs             769332      12    769320   1% /run/shm
# /dev/mmcblk0p1     57288   23272     34016  41% /boot
#
# df  /run/shm/pi/database.db
# Filesystem     1K-blocks  Used Available Use% Mounted on
# tmpfs             769332    12    769320   1% /run/shm
#
def GetDiskUsagePct(dirOrFile):
    retVal = None

    output = None
    try:
        # get second line, 4th index (Use%), chars up to but not including % sign
        outStr     = subprocess.check_output(("df %s" % DirectoryPart(dirOrFile)).split()).decode()
        secondLine = outStr.splitlines()[1]
        retVal     = int(secondLine.split()[4][:-1])

    except Exception as e:
        pass
        
    return retVal







