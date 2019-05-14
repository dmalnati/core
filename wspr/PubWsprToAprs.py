#!/usr/bin/python -u

import os
import subprocess
import time
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *

from libDbWSPR import *
from libAPRS import *


class App:
    def __init__(self, user, password, intervalSec, startMode):
        # Basic object configuration
        self.user        = user
        self.password    = password
        self.intervalSec = intervalSec
        
        # state keeping
        self.call__recTdList = dict()
        self.dateLast        = ""
        self.count           = 0
        
        Log("Configured for:")
        Log("  user        = %s" % self.user)
        Log("  password    = %s" % self.password)
        Log("  intervalSec = %s" % intervalSec)
        Log("  startMode   = %s" % startMode)
        Log("")
        
        # get handles to database
        self.db  = DatabaseWSPR()
        self.td  = self.db.GetTableDownload()
        self.tnv = self.db.GetTableNameValue()
        
        # handle cold start
        if startMode == "cold":
            rowIdLast = self.GetLast()
            
            Log("    Resetting last processed to -1 from %s" % rowIdLast)
            Log("")
            
            self.SetLast(-1)
        
    def GetLast(self):
        rec = self.tnv.GetRecordAccessor()
        if self.tnv.Count() == 0:
            rec.Set("NAME", "LAST_PROCESSED")
            rec.Set("VALUE", "-1")
            rec.Insert()
        
        rec.Set("NAME", "LAST_PROCESSED")
        rec.Read()
        retVal = int(rec.Get("VALUE"))
        
        return retVal
        
    def SetLast(self, rowid):
        rec = self.tnv.GetRecordAccessor()
        
        rec.Set("NAME", "LAST_PROCESSED")
        rec.Read()
        rec.Set("VALUE", str(rowid))
        
        retVal = rec.Update()
        
        return retVal
        
        
    def Post(self, loginStr, aprsMsg):
        url = "http://rotate.aprs.net:8080"
    
        postData      = str(loginStr) + "\n" + str(aprsMsg)
        contentLength = len(postData)
        
        procAndArgs = [
            'curl', \
            '-k', \
            '-i', \
            '-w', \
            '-L', \
            '-X', 'POST', \
            '-H', 'Accept-Type: text/plain', \
            '-H', 'Content-Type: application/octet-stream', \
            '-H', 'Content-Length: ' + str(contentLength), \
            '-d', postData, \
            url \
        ]
        
        Log("curl cmd: " + str(procAndArgs))
    
        byteList = subprocess.check_output(procAndArgs)
        
        Log("ret: " + str(byteList))

        
    def Upload(self, aprsMsg):
        loginStr = "user %s pass %s vers TestSoftware 1.0" % (self.user, self.password)
        #aprsMsg  = "KN4IUD-11>WSPR,TCPIP*:/225418h2646.53N/08259.54WO294/010/A=008810 MM17  ) !',$   #"
    
        self.Post(loginStr, aprsMsg)


    
    
    
    def OnUpdate(self, recTd):
        # assume updates are in chronological order
        # we want to know when we've seen the last of a 2-minute bucket
        date = recTd.Get("DATE")
        
        if self.dateLast != "" and self.dateLast != date:
            # the time has changed, batch process all stored data
            self.OnAllUpdatesThisPeriodComplete()
            
            self.call__recTdList = dict()
            self.count           = 0
            
        self.count += 1
        
        # keep track of the time, if it changed, you've handled it by now
        self.dateLast = date
        
        # keep state for this time period
        self.OnUpdateRec(recTd)
    

    def OnUpdateRec(self, recTd):
        call = recTd.Get("CALLSIGN")
        
        if call not in self.call__recTdList:
            self.call__recTdList[call] = []
            
        self.call__recTdList[call].append(recTd)
        
    def GetAltitudeFtFromPower(self, power):
        tupleList = [
           (  "0",     0 ),  
           (  "3",  2222 ),  
           (  "7",  4444 ),  
           ( "10",  6667 ),  
           ( "13",  8889 ),  
           ( "17", 11111 ),  
           ( "20", 13333 ),  
           ( "23", 15556 ),  
           ( "27", 17778 ),  
           ( "30", 20000 ),  
           ( "33", 22222 ),  
           ( "37", 24444 ),  
           ( "40", 26667 ),  
           ( "43", 28889 ),  
           ( "47", 31111 ),  
           ( "50", 33333 ),  
           ( "53", 35556 ),  
           ( "57", 37778 ),  
           ( "60", 40000 )
        ]
        
        power__altFt = dict(tupleList)
        
        # the power parameter is +27, etc
        # we want 27
        # so strip
        powerLookup = power[1:]
        
        retVal = 0
        if powerLookup in power__altFt:
            retVal = power__altFt[powerLookup]
            
        return retVal

        
    # DOWNLOAD[11680]
    #   DATE     : 2019-05-13 02:20
    #   CALLSIGN : 8P9DH
    #   FREQUENCY: 14.097130
    #   SNR      : -23
    #   DRIFT    : 0
    #   GRID     : GK03
    #   DBM      : +37
    #   WATTS    : 5.012
    #   REPORTER : WA2ZKD
    #   RGRID    : FN13ed
    #   KM       : 3748
    #   MI       : 2329
    #
    #  KN4IUD-11>WSPR,TCPIP*:/225418h2646.53N/08259.54WO294/010/A=008810 MM17  ) !',$   #
    #
    def OnAllUpdatesThisPeriodComplete(self):
        Log("")
        Log("Changes this period: %s" % self.dateLast)
        for call in self.call__recTdList.keys():
            recTdList = self.call__recTdList[call]
            
            # determine:
            # furthest signal
            #   reporter at furthest signal
            # best SNR
            #   frequency at best SNR
            distMiMax    = 0
            reporterBest = "UNKN"
            snrMax       = 0
            freqBest     = 0
            for recTd in recTdList:
                distMi = recTd.Get("MI")
                if distMi > distMiMax:
                    distMiMax    = distMi
                    reporterBest = recTd.Get("REPORTER")
            
                snr = recTd.Get("SNR")[1:]
                if snr > snrMax:
                    snrMax = snr
                    freqBest = recTd.Get("FREQUENCY")
            
            # reference using the first element
            recTd = recTdList[0]
            
            recTd.DumpVertical(Log)
            Log("")
            
            amm = APRSMessageMaker()

            wsprCall = call
            ssid     = 15
            wsprDate = recTd.Get("DATE")
            wsprGrid = recTd.Get("GRID")
            altitudeFt = self.GetAltitudeFtFromPower(recTd.Get("DBM"))
            
            extraData  = ""
            extraData +=       recTd.Get("DATE")
            extraData += " " + distMiMax + "mi"
            extraData += " " + reporterBest
            extraData += " " + snrMax
            extraData += " " + freqBest
            msg = amm.MakeLocationReportMessage(wsprCall, ssid, wsprDate, wsprGrid, altitudeFt, extraData)
            
            Log("%s : %s" % (call, len(recTdList)))
            Log(amm.GetRefStrNoSSID())
            Log(msg)
            
            #self.Upload(msg)


    def Process(self):
        Log("Scanning DOWNLOAD for new spots")
        
        # Prepare to walk records
        recTd = self.td.GetRecordAccessor()
        recTd.SetRowId(self.GetLast())
        
        Log("  Starting from rowid %s" % recTd.GetRowId())
        
        # Walk list of records starting from last seen
        count = 0
        timeStart = DateTimeNow()
        while recTd.ReadNextInLinearScan():
            count += 1
            self.OnUpdate(recTd)
        
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        Log("  Scan took %s sec" % Commas(secDiff))
        Log("  Saw %s new records" % Commas(count))
        
        if count != 0:
            rowId = recTd.GetRowId()
            Log("    Saving %s as last rowid seen" % rowId)
            self.SetLast(rowId)
    
    
    def OnTimeout(self):
        timeStart = DateTimeNow()
        self.Process()
        timeEnd = DateTimeNow()
        
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        timeoutMs = self.intervalSec * 1000
        
        Log("Waking in %s sec" % str(timeoutMs // 1000))
        Log("")
        
        evm_SetTimeout(self.OnTimeout, timeoutMs)
        
    def OnStdIn(self, str):
        pass
        
    def Run(self):
        def OnStdIn(inputStr):
            inputStr = inputStr.strip()

            if inputStr != "":
                self.OnKeyboardReadable(inputStr)
            
        WatchStdinEndLoopOnEOF(OnStdIn, binary=True)

        evm_SetTimeout(self.OnTimeout, 0)
        
        Log("Running")
        Log("")
        
        evm_MainLoop()

    
    

def Main():
    LogIncludeDate(True)
    
    # default arguments
    intervalSec = 30
    startMode   = "warm"

    if len(sys.argv) < 3 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <user> <pass> <intervalSec=%s> <startMode=%s>" % (sys.argv[0], intervalSec, startMode))
        sys.exit(-1)

    user     = sys.argv[1]
    password = sys.argv[2]
    
    # pull out arguments
    if len(sys.argv) >= 4:
        intervalSec = int(sys.argv[3])

    if len(sys.argv) >= 5:
        startMode = sys.argv[4]
        
    # create and run app
    app = App(user, password, intervalSec, startMode)
    app.Run()



Main()












