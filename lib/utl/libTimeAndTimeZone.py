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
        
        self.timeNative = datetime.datetime.strptime(self.timeStr, self.formatStr)
        self.timeNative = pytz.timezone(timeZoneStr).localize(self.timeNative)
        
    def GetTimeNative(self):
        return self.timeNative
        
    def GetTimeNativeInTimeZone(self, timeZoneStr):
        return self.timeNative.astimezone(pytz.timezone(timeZoneStr))

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
