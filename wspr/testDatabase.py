#!/usr/bin/python -u

from libDbWSPR import *



def Main():
    db = DatabaseWSPR()
    
    #print("GetFieldList: %s" % GetFieldList())
    #print("GetSchema: %s" % GetSchema())
    
    
    td = db.GetTableDownload()
    
    #rec = td.CreateRecord()
    
    
    
Main()



"""

Overall design:
---------------

Downloader keeps a 1 hour rolling window of WSPR activity.
Filterer monitors new, plucks out and stores ones that are me.
Uploader monitors filtered output, uploads and deletes filter record.




What I need to be able to do:

From downloader
---------------

Populate a given record
See if it's already in the database
Insert



From Filterer
-------------

Check what records are new




"""




















