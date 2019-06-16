import os
import sys


def CorePath(path):
    core = os.environ["CORE"]

    return core + path


def MoveToCoreRuntimeDir():
    os.chdir(CorePath('/runtime'))


def ApplyEnvironmentMapToThisProcess():
    envMap = GetEnvironmentMap()

    for key in envMap:
        os.environ[key] = envMap[key]

        if key == 'PYTHONPATH':
            for val in envMap[key].split(':'):
                sys.path.append(val)

#
# Create the necessary environment variable values necessary for the system to
# run and return as a dict.
#
# This includes:
# - PATH
# - PYTHONPATH
# - CORE_CFG_PATH
#
def GetEnvironmentMap():
    envMap = dict()

    # get list of product directories, reversed.
    # we're going to peel off front-to-back, so we want the
    # core product to end up last so it's the most preferred in the various
    # lists of paths we're creating
    productDirList = GetProductDirectoryListReversed()

    # Set up PATH
    val = ''
    if 'PATH' in os.environ:
        val = os.environ['PATH']

    for productDir in productDirList:
        for subdir in ['%s/test' % productDir, '%s/scripts' % productDir]:
            if val.find(subdir + ':') == -1:
                val = subdir + ':' + val

    envMap['PATH'] = val


    # Set up PYTHONPATH
    val = ''
    if 'PYTHONPATH' in os.environ:
        val = os.environ['PYTHONPATH']

    for productDir in productDirList:
        libDir = productDir + '/lib'

        for path, subDirListGen, fileList in os.walk(libDir, followlinks = True):
            subDirList = sorted(subDirListGen)
            subDirList.insert(0, '')

            for subDir in subDirList:
                if subDir != '':
                    fullSubDir = path + '/' + subDir
                else:
                    fullSubDir = path

                if fullSubDir.find('__pycache__') == -1:
                    if val.find(fullSubDir + ':') == -1:
                        val = fullSubDir + ':' + val

    envMap['PYTHONPATH'] = val


    # Set up CORE_CFG_PATH
    envMap['CORE_CFG_PATH'] = CorePath('/site-specific/cfg') + ':' + CorePath('/generated-cfg')


    return envMap



NON_PRODUCT_SUBDIR_LIST = [
    "/archive",
    "/generated-cfg",
    "/site-specific",
    "/site-specific/cfg",
    "/runtime",
    "/runtime/db",
    "/runtime/logs",
    "/runtime/logs/currentRun",
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

def GetProductListReversed():
    return GetProductList()[::-1]

def GetProductDirectoryListReversed():
    return GetProductDirectoryList()[::-1]


def GetNonProductDirectoryList():
    directoryList = []

    core = os.environ["CORE"]

    for nonProductSubdir in NON_PRODUCT_SUBDIR_LIST:
        directoryList.append(core + nonProductSubdir)

    return directoryList


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
