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
    url += "&band=all"
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
    soup = BeautifulSoup(byteList, 'html.parser')
    
    # Get the number of spots in the database, total
    # table 1
    #   row 1
    #     column 5
    
    spotStr = soup.find_all('table')[0].find_all('tr')[0].find_all('td')[4].contents[0].split()[0]
    
    print("spots: %s" % (spotStr))
    
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
    
    # fill out record
    db = DatabaseWSPR()
    t = db.GetTableDownload()
    rec = t.GetRecordAccessor()
    
    # wipe out all the old records
    rec.StartLinearScan()
    
    while rec.GetNext():
        print(rec.Get('DBM'))
        
    
    # add new records
    rec.Reset()
    for trData in trDataList:
        valList = map(lambda x : strip_non_ascii(x.contents[0]), trData.find_all('td'))
        
        print(valList)
        
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
        
        print("DBM: %s" % rec.Get("DBM"))
        
        if rec.RecordExistsInDatabase() == False:
            rec.Insert()
    
    
def file_get_contents(filename):
    with open(filename) as f:
        return f.read()


def Main():
    limit = 50
    url   = MakeWSPRUrl(limit)

    print("url: %s" % url)
    
    #byteList = GetDataAtUrl(url)
    byteList = file_get_contents("testInput.txt")
    print("byteListLen: %i" % len(byteList))
    
    #print("byteList: %s" % byteList)
    
    ParseWsprSpotFromOldDatabaseHtml(byteList)
    



Main()
















