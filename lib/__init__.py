import os

#every sub-directory is a library we care about

__all__ = []

for (thisDir, subDirList, fileList) in os.walk('.'):
    for subDir in subDirList:
        __all__.append(subDir)
