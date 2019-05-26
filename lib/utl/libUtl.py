import time
import datetime
import binascii

import json


#######################################################################
#
# Utility
#
#######################################################################


def DateNow():
    formatStr = "%Y-%m-%d"

    return datetime.datetime.now().strftime(formatStr)

def TimeNow():
    return datetime.datetime.now().time().isoformat()

def DateTimeNow():
    formatStr = "%Y-%m-%d %H:%M:%S.%f"
    
    return datetime.datetime.now().strftime(formatStr)

    
def DateTimeStrDiffSec(dtStr1, dtStr2):
    formatStr = "%Y-%m-%d %H:%M:%S"
    
    # drop any trailing microsecond values, we don't care
    # about that here
    dtStr1New = dtStr1.split(".")[0]
    dtStr2New = dtStr2.split(".")[0]

    dt1 = datetime.datetime.strptime(dtStr1New, formatStr)
    dt2 = datetime.datetime.strptime(dtStr2New, formatStr)
    
    dtDiff = dt1 - dt2
    
    secDiff = int(dtDiff.total_seconds())
    
    return secDiff
    
def SecsToDuration(secs):
    return str(datetime.timedelta(seconds=secs))
    
logDateAlso = False

def LogIncludeDate(yesNo):
    global logDateAlso

    logDateAlso = yesNo

def Log(msg):
    global logDateAlso

    logStr = ""
    logStr += "["

    if logDateAlso:
        logStr += datetime.datetime.today().strftime('%Y-%m-%d')
        logStr += " "

    logStr += str(TimeNow())
    logStr += "]: "
    logStr += str(msg)

    print(logStr)

def LogCsv(msg):
    global logDateAlso

    logStr = ""

    if logDateAlso:
        logStr += datetime.datetime.today().strftime('%Y-%m-%d')
        logStr += ", "

    logStr += str(TimeNow())
    logStr += ", "
    logStr += msg

    print(logStr)


def Commas(strToFormat):
    return "{:,}".format(int(strToFormat))
    
    
def GetPrettyJSON(jsonObj):
    return json.dumps(jsonObj,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))




# slightly re-arranged from code found here:
# http://www.evilgeniuslair.com/2015/01/14/crc-8/
class CRC8:
    def __init__(self):
        pass

    @staticmethod
    def Calculate(buf):
        return CRC8.calcCheckSum(buf)

    @staticmethod
    def calcCheckSum(incoming):
        #msgByte = hexStr2Byte(incoming)
        msgByte = bytearray(incoming)
        check = 0
        for i in msgByte:
            check = CRC8.AddToCRC(i, check)
        return check

    @staticmethod
    def AddToCRC(b, crc):
        b2 = b
        if (b < 0):
            b2 = b + 256
        for i in xrange(8):
            odd = ((b2^crc) & 1) == 1
            crc >>= 1
            b2 >>= 1
            if (odd):
                crc ^= 0x8C # this means crc ^= 140
        return crc



#http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
class Bunch(dict):
    def __init__(self, **kwds):
        dict.__init__(self, kwds)
        self.__dict__.update(kwds)











