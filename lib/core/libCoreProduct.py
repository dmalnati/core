import os






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


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    