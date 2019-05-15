import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *

        
        
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
        
