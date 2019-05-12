#!/usr/bin/python -u

import os
import subprocess
import time
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *

from libDbWSPR import *

from bs4 import BeautifulSoup


def GetDataAtUrl(url):
    byteList = subprocess.check_output(['wget', '-qO-', url])
    
    return byteList
    
# 
def MakeWSPRUrl(limit):
    url  = "http://wsprnet.org/olddb"
    url += "?mode=html"
    #url += "&band=all"
    url += "&band=20"
    url += "&limit=%i" % (limit)
    url += "&findcall="
    url += "&findreporter="
    url += "&sort=date"

    return url

# https://repl.it/@nickangtc/python-strip-non-ascii-characters-from-string
def strip_non_ascii(string):
        ''' Returns the string without non ASCII characters'''
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)
        
    
def ParseWsprSpotFromOldDatabaseHtml(byteList):

    Log("Parsing downloaded file")
    timeStart = DateTimeNow()
    #soup = BeautifulSoup(byteList, 'html.parser')  ;# 56 sec
    soup = BeautifulSoup(byteList, 'lxml') ;# 54 sec
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
    
    # Get the number of spots in the database, total
    # table 1
    #   row 1
    #     column 5
    
    spotStr = soup.find_all('table')[0].find_all('tr')[0].find_all('td')[4].contents[0].split()[0]
    
    # Get all the spots
    # table 3
    #
    # the first two rows are headers
    # after that it's data
    #
    # 12 columns of data (ignore the goofy double header rows)
    #                                                         Power,       Reported,     Distance
    # Date,             Call,  Frequency, SNR, Drift, Grid,   dBm, W,     by,   loc,    km,   mi
    # 2019-05-11 23:58, W6LVP, 7.040035,  -28, 0,     DM04li, +37, 5.012, K2JY, EM40xa, 2762, 1716
    # ...
    #
    
    trList = soup.find_all('table')[2].find_all('tr')
    
    trHeader   = trList[1]
    trDataList = trList[2:]
    
    Log("  Parsing took %s seconds" % secDiff)
    Log("  WSPRnet Spot Count: %s" % Commas(spotStr))
    Log("    %s Records downloaded (%s rec/sec)" % (Commas(len(trDataList)), Commas(len(trDataList) // secDiff)))
    Log("")
    
    
    # fill out record
    db = DatabaseWSPR()
    t = db.GetTableDownload()
    rec = t.GetRecordAccessor()
    
    Log("Local cache starting count: %s" % Commas(t.Count()))
    Log("")
    
    # wipe out all the old records
    ONE_HOUR_IN_SECONDS = 60 * 60
    Log("Removing records older than 1 hour")

    timeStart = DateTimeNow()
    timeNow = timeStart
    deleteCount = t.DeleteOlderThan(ONE_HOUR_IN_SECONDS)
    #deleteCount = 0
    #while rec.ReadNextInLinearScan():
    #    ts = rec.Get("TIMESTAMP")
    #    
    #    secDiff = DateTimeStrDiffSec(timeNow, ts)
    #    
    #    if secDiff >= ONE_HOUR_IN_SECONDS:
    #        rec.Delete()
    #        deleteCount += 1
    
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
    
    Log("Deleted %s records" % Commas(deleteCount))
    Log("  Removing took %s seconds" % secDiff)
    Log("")
    
    # add new records
    Log("Updating with new records")
    timeStart = DateTimeNow();
    
    db.BatchBegin()
    
    rec.Reset()
    insertCount = 0
    for trData in trDataList:
        valList = map(lambda x : strip_non_ascii(x.contents[0]), trData.find_all('td'))
        
        rec.Set("DATE",      valList[0])
        rec.Set("CALLSIGN",  valList[1])
        rec.Set("FREQUENCY", valList[2])
        rec.Set("SNR",       valList[3])
        rec.Set("DRIFT",     valList[4])
        rec.Set("GRID",      valList[5])
        rec.Set("DBM",       valList[6])
        rec.Set("WATTS",     valList[7])
        rec.Set("REPORTER",  valList[8])
        rec.Set("RGRID",     valList[9])
        rec.Set("KM",        valList[10])
        rec.Set("MI",        valList[11])
        
        #if rec.Read() == False:
        if rec.Insert():
            insertCount += 1
    
    db.BatchEnd()
    
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
    
    Log("Inserted %s records" % Commas(insertCount))
    Log("  Inserting took %s seconds" % secDiff)
    
    Log("")
    Log("Local cache ending count: %s" % Commas(t.Count()))
    Log("")
    
    
def file_get_contents(filename):
    with open(filename) as f:
        return f.read()


def Main():
    LogIncludeDate(True)

    limit = 1000
    url   = MakeWSPRUrl(limit)

    Log("Downloading latest %s spots from WSPRnet" % Commas(limit))
    
    
    timeStart = DateTimeNow()
    byteList = GetDataAtUrl(url)
    #byteList = file_get_contents("testInput.txt")
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
    Log("  Download took %i seconds -- %s bytes" % (secDiff, Commas(len(byteList))))
    Log("")
    
    ParseWsprSpotFromOldDatabaseHtml(byteList)
    


while True:
    Main()
















