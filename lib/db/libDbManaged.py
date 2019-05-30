from libEvm import *
from libWSApp import *
from libDb import *


#
# Users should
#
# self.db = ManagedDatabase(self)
# self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
# 
# def OnDatabaseStateChange(state)
#   if state == "DATABASE_AVAILABLE":
#       self.OnDoDatabaseStuff()
#   if state == "DATABASE_CLOSING":
#       self.OnDoFinalCleanup()
#
#
class ManagedDatabase(Database, WSEventHandler):
    def __init__(self, wsApp):
        Database.__init__(self)
        
        self.wsApp = wsApp
        
        self.cbFn  = None
        self.dbSvc = SysDef.Get("CORE_DATABASE_MANAGER_SERVICE")
        
        self.dbState = None
    
    def SetCbOnDatabaseStateChange(self, cbFn):
        self.cbFn = cbFn
        
        Log("Connecting to %s for database state" % self.dbSvc)
        self.wsApp.Connect(self, self.dbSvc)

    def OnDatabaseAvailable(self, dbFullPath):
        if self.Connect(forcedDbFullPath = dbFullPath):
            self.cbFn("DATABASE_AVAILABLE")
        
    def OnDatabaseClosing(self):
        self.cbFn("DATABASE_CLOSING")
        
        evm_MainLoopFinish()
        

    ######################################################################
    #
    # Implementing WSNodeMgr Events
    #
    ######################################################################

    def OnConnect(self, ws):
        Log("Connected to %s" % self.dbSvc)

    def OnMessage(self, ws, msg):
        state      = None
        dbFullPath = None
        
        try:
            if msg["MESSAGE_TYPE"] == "DATABASE_STATE":
                state      = msg["STATE"]
                dbFullPath = msg["DATABASE_PATH"]
        except Exception as e:
            Log("ERR: State connection message handler error: %s" % e)
            ws.DumpMsg(msg)

        if state and dbFullPath:
            if state == "DATABASE_AVAILABLE":
                self.OnDatabaseAvailable(dbFullPath)
            elif state == "DATABASE_CLOSING":
                self.OnDatabaseClosing()

    def OnClose(self, ws):
        Log("Connection lost to %s, exiting" % self.dbSvc)
        evm_MainLoopFinish()

        
    def OnError(self, ws):
        Log("Couldn't connect to %s, trying again" % (self.dbSvc))
    
    
    
    
    
    
    
    
    
    
    
    