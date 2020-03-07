import datetime
import pytz


#
# https://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/
# http://pytz.sourceforge.net/#localized-times-and-date-arithmetic
# https://stackoverflow.com/questions/2720319/python-figure-out-local-timezone
#
class TimeAndTimeZone():
    def __init__(self):
        self.timeStr    = None
        self.timeNative = None
        self.formatStr  = None
    


    # Static
    def ParseAndGetTimeNativeInTimeZone(self, timeStr, formatStr, timeZoneStr):
        timeNative = datetime.datetime.strptime(timeStr, formatStr)
        timeNativeInTz = self.ConvertNativeToTimezone(timeNative, timeZoneStr)
        return timeNativeInTz

    # Static
    def Now(self):
        tzLocal = self.GetTimeZoneLocal()
        timeNative = datetime.datetime.now()
        timeNativeInTz = self.ConvertNativeToTimezone(timeNative, tzLocal)

        return timeNativeInTz

    # Static
    def ConvertNativeToTimezone(self, nativeDatetime, timeZoneStr):
        return pytz.timezone(timeZoneStr).localize(nativeDatetime).astimezone(pytz.timezone(timeZoneStr))

    # Static
    def GetTimeZoneLocal(self):
        return str(datetime.datetime.now(datetime.timezone(datetime.timedelta(0))).astimezone().tzinfo)



    def SetTime(self, timeStr, formatStr, timeZoneStr):
        self.timeStr    = timeStr
        self.timeNative = None
        self.formatStr  = formatStr
        
        #self.timeNative = datetime.datetime.strptime(self.timeStr, self.formatStr)
        self.timeNative = datetime.datetime.strptime(self.timeStr, self.formatStr)
        self.timeNative = pytz.timezone(timeZoneStr).localize(self.timeNative)
        
    def GetTimeNative(self):
        return self.timeNative
        
    def GetTimeNativeInTimeZone(self, timeZoneStr):
        return self.timeNative.astimezone(pytz.timezone(timeZoneStr))

    def GetValidTimeString(self, str):
        # I want "YYYY-MM-DD HH:MM:SS"

        strTemplate = "0000-01-01 00:00:00"
        strTemplateLen = len(strTemplate)

        strAdjusted = str
        strAdjustedLen = len(str)

        # ensure equal number of characters
        if strAdjustedLen > strTemplateLen:
            # truncate
            strAdjusted = strAdjusted[:strTemplateLen]
        elif strAdjustedLen < strTemplateLen:
            # extend with spaces
            strAdjusted += ((strTemplateLen - strAdjustedLen) * " ")

        # now anywhere that there isn't a value, make sure there is one.
        # this doesn't protect against completely invalid datetimes
        # but could be extended to do so later.
        strFinal = ""
        for charGood, charMaybe in zip(strTemplate, strAdjusted):
            if charMaybe != " ":
                strFinal += charMaybe
            else:
                strFinal += charGood

        return strFinal
        
        
        
        
        
        
        
        
        
        
        
        
