# every file in this dir is a module we want to import

import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    else:
        exec("from " + module[:-3] + " import *")

del module
