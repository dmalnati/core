import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *




class APRSMessageMaker:
    def __init__(self):
        pass
    
    def GetRefStr(self):
        return "KN4IUD-11>WSPR,TCPIP*:/225418h2646.53N/08259.54WO294/010/A=008810 MM17  ) !',$   #"
    
    def GetRefStrNoSSID(self):
        return "KN4IUD>WSPR,TCPIP*:/225418h2646.53N/08259.54WO294/010/A=008810 MM17  ) !',$   #"
    
    def MakeLocationReportMessage(self, call, ssid, wsprDate, grid, altitudeFt, extraData = ""):
        # Basic APRS message
        callsign           = call
        ssid               = str(ssid)
        receivedBy         = "WSPR"
        timeOfReceptionUtc = self.GetTimeUtc(wsprDate)
        latitudeStr        = self.ConvertGridToAPRSLatitude(grid)
        symbolTableId      = "/"    ;# table 1
        longitudeStr       = self.ConvertGridToAPRSLongitude(grid)
        symbolCode         = "O"    ;# balloon
        courseDegs         = self.GetCourseDegs(0)
        speedKnots         = self.GetSpeedKnots(0)
        altitudeFt         = self.ConvertAltitudeFtToAPRSFeet(altitudeFt)
        
        # Encoded data fun to slot in
        # ...

        # Construct message
        msg  = ""
        msg += callsign + "-" + ssid
        msg += ">"
        msg += receivedBy
        msg += ",TCPIP*"
        msg += ":"
        msg += "/"
        msg += timeOfReceptionUtc
        msg += latitudeStr
        msg += symbolTableId
        msg += longitudeStr
        msg += symbolCode
        msg += courseDegs
        msg += speedKnots
        msg += altitudeFt
        
        # There are now 43 bytes remaining for comment
        # Testing shows you can add as much arbitrary data as you want.
        # There are no rules on TCPIP uploads it seems, just do whatever.
        msg += extraData
        
        return msg
        
        

    #################################################
    ##
    ## Time
    ##
    #################################################

    def GetTimeUtc(self, wsprDate):
        partList = wsprDate.split(" ")[1].split(":")  ;# 2019-05-13 02:20 to [02 20]
        timeUtc = "".join(partList) + "00h"           ;# now 022000h
        
        return timeUtc
    
    
    #################################################
    ##
    ## Latitude and Longitude
    ##
    #################################################
    
    def ConvertLatLngToDegreesMinutesSeconds(self, latOrLongInMillionths):
        ONE_MILLION     = 1000000
        MIN_PER_DEGREE  = 60
        SECONDS_PER_MIN = 60
        
        # Capture input value for manipulation
        valRemaining = float(latOrLongInMillionths)                    ;# eg 40736878
        
        # Calculate degrees
        degrees = int(valRemaining // ONE_MILLION)                     ;# eg 40
        
        # Calculate minutes by converting millionths of a degree
        valRemaining = abs(valRemaining) - \
                       (abs(degrees) * ONE_MILLION)                   ;# eg   736878
        
        valRemaining = (valRemaining / ONE_MILLION) * MIN_PER_DEGREE  ;# eg   44.21268
        
        minutes = int(valRemaining)                                   ;# eg 44
        
        # Calculate seconds by converting the fractional minutes
        valRemaining -= minutes                                       ;# eg .21268
        
        valRemaining *= SECONDS_PER_MIN                               ;# eg 12.7608
        
        seconds = valRemaining                                        ;# eg 12.7608
        
        return degrees, minutes, seconds

        
    #################################################
    ##
    ## Latitude
    ##
    #################################################
    
    def ConvertGridToAPRSLatitude(self, grid):
        latMillionths = self.GetLatitudeFromGrid(grid)
        
        degrees, minutes, seconds = self.ConvertLatLngToDegreesMinutesSeconds(latMillionths)
        
        aprsStr = self.ConvertLatitudeFromDegMinSecToDegMinHundredths(degrees, minutes, seconds)
        
        return aprsStr
    
    
    def GetLatitudeFromGrid(self, grid):
        lat  = 0
        lat += (ord(grid[1]) - ord('A')) * 100000
        lat += (ord(grid[3]) - ord('0')) *  10000
        
        if len(grid) >= 6:
            lat += (ord(grid[5]) - ord('A')) *    417
        
        lat -= (90 * 10000)
        
        lat *= 100  ; # in millions of a degree
        
        return lat

    #
    # The latitude is shown as the 8-character string
    # ddmm.hhN (i.e. degrees, minutes and hundredths of a minute north)
    #
    # ex: 4903.50N is 49 degrees 3 minutes 30 seconds north
    #
    def ConvertLatitudeFromDegMinSecToDegMinHundredths(self, degrees, minutes, seconds):
        # Constrain values
        if degrees < -90:
            degrees = -90
        
        if degrees > 90:
            degrees = 90
            
        if minutes > 59:
            minutes = 59
            
        if seconds > 59:
            seconds = 59
            
        
        # Calculate values
        northOrSouth = "S"
        if degrees >= 0:
            northOrSouth = "N"
        
        degreesPos          = int(abs(degrees))
        secondsAsHundredths = int(round(seconds / 60.0 * 100.0))
        
        if secondsAsHundredths == 100:
            secondsAsHundredths = 99
        
        str = "%02i%02i.%02i%c" % (degreesPos, minutes, secondsAsHundredths, northOrSouth)
        
        return str
    
    
    #################################################
    ##
    ## Longitude
    ##
    #################################################
    
    def ConvertGridToAPRSLongitude(self, grid):
        lngMillionths = self.GetLongitudeFromGrid(grid)
        
        degrees, minutes, seconds = self.ConvertLatLngToDegreesMinutesSeconds(lngMillionths)
        
        aprsStr = self.ConvertLongitudeFromDegMinSecToDegMinHundredths(degrees, minutes, seconds)
        
        return aprsStr
        
    
    def GetLongitudeFromGrid(self, grid):
        lng  = 0
        lng += (ord(grid[0]) - ord('A')) * 200000
        lng += (ord(grid[2]) - ord('0')) *  20000
        
        if len(grid) >= 5:
            lng += (ord(grid[4]) - ord('A')) *    834
        
        lng -= (180 * 10000)
        
        lng *= 100  ; # in millions of a degree
        
        return lng
        
    #
    # The longitude is shown as the 9-character string
    # dddmm.hhW (i.e. degrees, minutes and hundredths of a minute west)
    #
    # ex: 07201.75W is 72 degrees 1 minute 45 seconds west
    #
    def ConvertLongitudeFromDegMinSecToDegMinHundredths(self, degrees, minutes, seconds):
        # Constrain values
        if degrees < -179:
            degrees = -179
            
        if degrees > 180:
            degrees = 180
            
        if minutes > 59:
            minutes = 59
        
        if seconds > 59:
            seconds = 59
        
        
        # Calculate values
        eastOrWest = "W"
        if degrees >= 0:
            eastOrWest = "E"
        
        degreesPos = int(abs(degrees))
        secondsAsHundredths = int(round(seconds / 60.0 * 100.0));
        
        if secondsAsHundredths == 100:
            secondsAsHundredths = 99
        
        str = "%03i%02i.%02i%c" % (degreesPos, minutes, secondsAsHundredths, eastOrWest)
        return str
        

    #################################################
    ##
    ## Course
    ##
    #################################################
        
    def GetCourseDegs(self, degs):
        str = "%03i" % (int(degs))
        
        return str
        
        
    #################################################
    ##
    ## Speed
    ##
    #################################################
        
    def GetSpeedKnots(self, speedKnots):
        str = "/%03i" % (int(speedKnots))
        
        return str
        

    #################################################
    ##
    ## Altitude
    ##
    #################################################
        
    def ConvertAltitudeFtToAPRSFeet(self, altitudeFt):
        str = "/A=%06i" % (altitudeFt)
        
        return str
        
        
        
        
        
        
        
        
        
        
        
        
class APRSUploader:
    def __init__(self, user, password):
        self.user     = user
        self.password = password
        
        
    def Upload(self, aprsMsg):
        loginStr = "user %s pass %s vers TestSoftware 1.0" % (self.user, self.password)

        postData      = str(loginStr) + "\n" + str(aprsMsg)
        contentLength = len(postData)
        
        url = "http://rotate.aprs.net:8080"
        
        procAndArgs = [
            'curl', \
            '-k', \
            '-i', \
            '-w', \
            '-L', \
            '-s', \
            '-X', 'POST', \
            '-H', 'Accept-Type: text/plain', \
            '-H', 'Content-Type: application/octet-stream', \
            '-H', 'Content-Length: ' + str(contentLength), \
            '-d', postData, \
            url \
        ]
        
        #Log(" ".join(procAndArgs))
        retVal = False
        try:
            #byteList = subprocess.check_output(procAndArgs)
            #Log("ret: " + str(byteList))
            
            retVal = True
        except:
            pass

        return retVal

        
        
#
# Takes in WSPR messages
# Converts to decoded structures
#
class WSPRDecoder:
    def __init__(self):
        pass
        
    def IsEligibleForUpload(self, name__value):
        retVal = False
        
        call = self.GetDecodedCallsign(name__value)
        if call == "KD2KDD":
            retVal = True
        
        return retVal
        
    def DecodeList(self, nvList):
        retVal = []
        
        for name__value in nvList:
            retVal.append(self.Decode(name__value))
        
        return retVal
        
    def Decode(self, name__valueInput):
        # first, assume all decoded fields are the same as input
        name__value = dict(name__valueInput)
        
        # now, go through rules to determine what fields to add/modify
        name__value["ALTITUDE_FT"] = self.GetDecodedAltitudeFt(name__valueInput)
        
        return name__value
        
    def GetDecodedCallsign(self, name__value):
        return name__value["CALLSIGN"]
        
    def GetDecodedAltitudeFt(self, name__value):
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
        
        # the power parameter is +27, etc.  we want 27, so strip
        power = name__value["DBM"]
        powerLookup = power[1:]
        
        retVal = 0
        if powerLookup in power__altFt:
            retVal = power__altFt[powerLookup]
            
        return retVal
        
        
        
        
class WsprToAprsBridge:
    def __init__(self, user, password):
        self.dateLast = ""
        self.nvList = []
        self.call__timeLastUploaded = dict()
        
        self.wsprDecoder  = WSPRDecoder()
        self.amm          = APRSMessageMaker()
        self.aprsUploader = APRSUploader(user, password)
        
        # set up default callbacks
        self.cbFnOnPreUpload      = self.DefaultCbFnOnPreUpload
        self.cbFnOnPeriodComplete = self.DefaultCbFnOnPeriodComplete
        self.cbOnRateLimit        = self.DefaultCbOnRateLimit
        
    def DefaultCbFnOnPreUpload(self, name__value, aprsMsg):
        fieldList = [
            'DATE',
            'CALLSIGN',
            'FREQUENCY',
            'SNR',
            'DRIFT',
            'GRID',
            'DBM',
            'WATTS',
            'REPORTER',
            'RGRID',
            'KM',
            'MI'
        ]
    
        nvStr = ""
        sep = ""
        for field in fieldList:
            nvStr += sep + str(name__value[field])
            sep = " "
    
        Log(nvStr)
        Log(aprsMsg)
    
    def SetCbFnOnPreUpload(self, cbFnOnPreUpload):
        self.cbFnOnPreUpload = cbFnOnPreUpload
        
    def DefaultCbFnOnPeriodComplete(self, period):
        Log("Period %s complete, processing uploads" % period)
        
    def SetCbFnOnPeriodComplete(self, cbFnOnPeriodComplete):
        self.cbFnOnPeriodComplete = cbFnOnPeriodComplete
    
    def DefaultCbOnRateLimit(self, call, secWait):
        Log("Sleeping %s sec due to rate limiting for %s" % (secWait, call))
    
    def SetCbOnRateLimit(self, cbOnRateLimit):
        self.cbOnRateLimit = cbOnRateLimit
    
    def Start(self):
        pass
        
    def Stop(self):
        self.OnAllUpdatesThisPeriodComplete()
        
    def OnUpdate(self, name__value):
        # assume updates are in chronological order
        # we want to know when we've seen the last of a 2-minute bucket
        date = name__value["DATE"]
        
        if self.dateLast != date and self.dateLast != "":
            # the time has changed, batch process all stored data
            if len(self.nvList):
                self.OnAllUpdatesThisPeriodComplete()
            
        # keep track of the time, if it changed, you've handled it by now
        self.dateLast = date
    
        if self.wsprDecoder.IsEligibleForUpload(name__value):
            # keep all eligible messages for this time period
            self.nvList.append(name__value)
            
            
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
        self.cbFnOnPeriodComplete(self.dateLast)
    
        # convert all cached
        nvDecodedList = self.wsprDecoder.DecodeList(self.nvList)
        
        # group by callsign
        call__nvList = dict()
        for nvDecoded in nvDecodedList:
            call = nvDecoded["CALLSIGN"]
            
            if call not in call__nvList.keys():
                call__nvList[call] = []
            
            call__nvList[call].append(nvDecoded)
    
        # iterate by callsign
        for call in call__nvList.keys():
            nvList = call__nvList[call]
            
            # determine:
            # furthest signal
            #   reporter at furthest signal
            # best SNR
            #   frequency at best SNR
            distMiMax    = 0
            reporterBest = "UNKN"
            snrMax       = 0
            freqBest     = 0
            for name__value in nvList:
                distMi = name__value["MI"]
                if distMi > distMiMax:
                    distMiMax    = distMi
                    reporterBest = name__value["REPORTER"]
            
                snr = name__value["SNR"][1:]
                if snr > snrMax:
                    snrMax = snr
                    freqBest = name__value["FREQUENCY"]
            
            # reference using the first element
            name__value = nvList[0]
            
            # construct APRS message
            wsprCall = call
            ssid     = 15
            wsprDate = name__value["DATE"]
            wsprGrid = name__value["GRID"]
            altitudeFt = name__value["ALTITUDE_FT"]
            
            # extra 43 bytes useful for whatever you want
            extraData  = ""
            extraData +=       name__value["DATE"]
            extraData += " " + distMiMax + "mi"
            extraData += " " + reporterBest
            extraData += " " + snrMax
            extraData += " " + freqBest
            
            msg = self.amm.MakeLocationReportMessage(wsprCall, ssid, wsprDate, wsprGrid, altitudeFt, extraData)
            
            # upload APRS message
            # but throttle to 1 upload per callsign to avoid server rate limiting
            if call in self.call__timeLastUploaded.keys():
                timeLast = self.call__timeLastUploaded[call]
                timeNow  = DateTimeNow()
                secsDiff = DateTimeStrDiffSec(timeNow, timeLast)
                
                # practical testing showed 1 per second seems to be ok
                if secsDiff < 1:
                    self.cbOnRateLimit(call, 1)
                    time.sleep(1)
            
            self.call__timeLastUploaded[call] = DateTimeNow()
            
            self.cbFnOnPreUpload(name__value, msg)
            
            self.aprsUploader.Upload(msg)        
        
        # reset state
        self.nvList = []

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        