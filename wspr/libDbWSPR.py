from libDb import *


class DatabaseWSPR(Database):
    databaseName = "wspr.db"

    def __init__(self):
        Database.__init__(self, self.databaseName)
        
        self.tableDownload = Table(self, "DOWNLOAD", self.GetSchema(), self.GetFieldListFromSchema(self.GetSchema()))
        
        
    def GetTableDownload(self):
        return self.tableDownload
        
        
    def GetSchema(self):
        return [
            ('DATE',      'text'),
            ('CALLSIGN',  'text'),
            ('FREQUENCY', 'text'),
            ('SNR',       'text'),
            ('DRIFT',     'text'),
            ('GRID',      'text'),
            ('DBM',       'text'),
            ('WATTS',     'text'),
            ('REPORTER',  'text'),
            ('RGRID',     'text'),
            ('KM',        'text'),
            ('MI',        'text')
        ]



        