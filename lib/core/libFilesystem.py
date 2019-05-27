import os
import sys
import shutil
import glob

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

