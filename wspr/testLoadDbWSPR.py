#!/usr/bin/python -u

import os
import sys

from libDbWSPR import *


def Main():
    if len(sys.argv) != 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <spotFileOldDb.txt>" % (sys.argv[0]))
        sys.exit(-1)

    # pull out arguments
    spotFile = sys.argv[1]
    
    # Access database
    db  = DatabaseWSPR()
    t   = db.GetTableDownload()
    rec = t.GetRecordAccessor()

    # Parse file contents
    byteList = []
    with open(spotFile) as f:
        byteList = f.read()
        
    lineList = sorted(byteList.split("\n"))
    
    timeStart = DateTimeNow()
    
    blankLineCount = 0
    badLineCount   = 0
    goodLineCount  = 0
    insertCount    = 0
    
    # Process each line as a record
    db.BatchBegin()
    
    for line in lineList:
        if len(line):
            linePartList = line.split()
            
            # need to combine the first two whitespace separated columns because
            # they together constitute the first field
            valList = []
            valList.append(linePartList[0] + " " + linePartList[1])
            valList.extend(linePartList[2:])
                
            if len(valList) == 12:
                goodLineCount += 1
                
                # store in database
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
                
                if rec.Insert():
                    insertCount += 1
            
            else:
                badLineCount += 1
        else:
            blankLineCount += 1
        
    db.BatchEnd()
    
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)

    if badLineCount:
        print("%s mismatched columns" % badLineCount)
    print("%s / %s inserted in %s sec" % (insertCount, goodLineCount, secDiff))
    
    
Main()













