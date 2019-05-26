#!/usr/bin/python -u


import os
import sys
import shutil

from shutil import copyfile

#
# Two modes of operation
# - first is to assist environment setup
#   - therefore libCore won't be available yet as the paths are being created
# - second is to run as actual installer
#   - libCore expected to exist at that time
#
try:
    from libCore import *
except:
    pass


NON_PRODUCT_SUBDIR_LIST = [
    "/archive",
    "/generated-cfg",
    "/site-specific",
    "/site-specific/cfg",
    "/runtime",
    "/runtime/logs",
    "/runtime/working",
]


def GetProductDirectoryList():
    core = os.environ["CORE"]

    nonProductDirectoryList = GetNonProductDirectoryList()
    productDirectoryList    = []
    coreProductDir          = core + "/core"

    for name in os.listdir(core):
        directory = core + "/" + name
        if os.path.isdir(directory):
            if directory not in nonProductDirectoryList:
                if directory != coreProductDir:
                    productDirectoryList.append(directory)

    # put in alphabetical order
    productDirectoryList.sort()

    # put core first
    productDirectoryList = [coreProductDir] + productDirectoryList

    return productDirectoryList

def GetProductList():
    productList = []

    for productDirectory in GetProductDirectoryList():
        product = os.path.basename(os.path.normpath(productDirectory))
        productList.append(product)

    return productList

def GetProductDirectoryListReversed():
    return GetProductDirectoryList()[::-1]


def GetNonProductDirectoryList():
    directoryList = []

    core = os.environ["CORE"]

    for nonProductSubdir in NON_PRODUCT_SUBDIR_LIST:
        directoryList.append(core + nonProductSubdir)

    return directoryList


def SetupDirectories():
    retVal = False

    Log("Setting up directories")

    directoryList = GetNonProductDirectoryList()

    try:
        for directory in directoryList:
            Log(directory)

            if not os.path.exists(directory):
                os.makedirs(directory)

        retVal = True
    except:
        pass

    if retVal:
        Log("  OK")
    else:
        Log("  NOT OK")

    return retVal


def SafeCopyFileIfExists(srcFile, dstFile):
    retVal = True

    if os.path.isfile(srcFile):
        try:
            copyfile(srcFile, dstFile)
        except:
            retVal = False

    return retVal
    

def RemoveDir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)

def MakeDir(directory):
    os.makedirs(directory)


def DeleteFilesInDir(directory):
    retVal = True

    for f in os.listdir(directory):
        try:
            fFullPath = directory + "/" + f
            if os.path.isfile(fFullPath):
                os.unlink(fFullPath)
        except:
            retVal = False

    return retVal


def CopyFiles(srcDir, dstDir, verbose = False):
    retVal = True

    if os.path.isdir(srcDir):
        for f in os.listdir(srcDir):
            if f[0] != '.':
                fFullPath = srcDir + "/" + f

                if os.path.isfile(fFullPath):
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


def MergeProductFilesToMaster(directory, fileSuffix, fileOut):
    productList = GetProductList()
    srcFileList = []

    # find all product files which match the file suffix
    for product in productList:
        fFullPath = directory + "/" + product + "_" + fileSuffix

        if os.path.isfile(fFullPath):
            srcFileList.append(fFullPath)

    # handle the special case of this being about ProcessDetails
    if fileSuffix == "ProcessDetails.json":
        cfgReader = ConfigReader()

        dataOut  = ""
        dataOut += "{ \"processDetailsList\" : ["

        # read in all the process details entries and merge to one master
        sep = ""
        for srcFile in srcFileList:
            cfg = cfgReader.ReadConfig(srcFile)

            processDetailList = cfg["processDetailsList"]
            for processDetail in processDetailList:
                processDetailStr = json.dumps(processDetail)

                dataOut += sep + processDetailStr

                sep = ","

        dataOut += "] }"

        # prettify output
        jsonObj = json.loads(dataOut)
        dataOutFormated = (json.dumps(jsonObj,
                                      sort_keys=True,
                                      indent=4,
                                      separators=(',', ': ')))

        # write output file
        fFullPath = directory + "/" + fileOut
        with open(fFullPath, 'w') as file:
            file.write(dataOutFormated)


# expected output format:
# <service> <host> <port> <wsPath>
def GenerateWSServices(directory):
    cfgReader = ConfigReader()
    cfg       = cfgReader.ReadConfig(directory + "/" + \
                                     "ProcessDetails.master.json")

    fFullPath = directory + "/" + "WSServices.txt"
    with open(fFullPath, 'w') as file:
        for processDetail in cfg["processDetailsList"]:
            entry  = ""
            entry +=       processDetail["name"]
            entry += " " + "127.0.0.1"
            entry += " " + str(1024 + int(str(processDetail["id"])))
            entry += " " + "/ws"

            file.write(entry + "\n")


def GenerateConfig():
    retVal = True

    Log("Assembling Configuration")
    Log("")

    core = os.environ["CORE"]

    productDirList = GetProductDirectoryListReversed()
    copyFromToList = []

    # make temporary directory after removing old if it exists
    tmpDir = core + "/generated-cfg/tmp"
    Log("Creating temporary folder %s" % tmpDir)
    RemoveDir(tmpDir)
    MakeDir(tmpDir)

    # Do file copies
    Log("Creating temporary file set")
    Log("")
    for productDir in productDirList:
        productCfgDir = productDir + "/cfg"
        retVal &= CopyFiles(productCfgDir, tmpDir, verbose=True)

    retVal &= CopyFiles(core + "/site-specific/cfg", tmpDir, verbose=True)

    # Do file generation
    Log("Generating ProcessDetials.master.json")
    MergeProductFilesToMaster(tmpDir,
                              "ProcessDetails.json",
                              "ProcessDetails.master.json")

    Log("Generating WSServices.txt")
    GenerateWSServices(tmpDir)

    Log("")


    # if successful, replace current gencfg with new
    # then remove temporary
    if retVal:
        gcDir = core + "/generated-cfg"

        Log("Assembly succssful, moving to %s" % gcDir)

        DeleteFilesInDir(gcDir)
        CopyFiles(tmpDir, gcDir)
        RemoveDir(tmpDir)
    else:
        Log("Failed to generate config properly")

    Log("")

    return retVal







def Main():
    retVal = True

    if len(sys.argv) > 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    if "CORE" in os.environ:
        if len(sys.argv) == 2 and sys.argv[1] == "-getProductDirListReversed":
            print(" ".join(GetProductDirectoryListReversed()))
        else:
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
                    retValSD = SetupDirectories()
                    Log("")
                    retValGC = GenerateConfig()

                    Log("DONE")

                    retVal = retValSD and retValGC
                else:
                    Log("State %s, needs to be CLOSED, quitting" % state)
                    retVal = False

                ss.ReleaseStateLock()
            else:
                Log("State locked, operation in progress elsewhere, quitting")
                retVal = False


    return retVal == False

sys.exit(Main())










