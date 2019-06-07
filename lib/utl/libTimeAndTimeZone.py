import datetime
import pytz


#
# https://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/
# http://pytz.sourceforge.net/#localized-times-and-date-arithmetic
#
class TimeAndTimeZone():
    def __init__(self):
        self.timeStr    = None
        self.timeNative = None
        self.formatStr  = None
        
    def SetTime(self, timeStr, formatStr, timeZone):
        self.timeStr    = timeStr
        self.timeNative = None
        self.formatStr  = formatStr
        
        self.timeNative = datetime.datetime.strptime(self.timeStr, self.formatStr)
        self.timeNative = pytz.timezone(timeZone).localize(self.timeNative)
        
    def GetTimeNative(self):
        return self.timeNative
        
    def GetTimeNativeInTimeZone(self, timeZone):
        return self.timeNative.astimezone(pytz.timezone(timeZone))

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
