import os
import sys

from libUtl import *
from libRun import *
from libSysDef import *
from libServerState import *
from libWSApp import *

import sqlite3
    

###############################################################################    
#
# db = Database()
# if db.Connect():
#     do stuff
#
###############################################################################

class Database():
    def __init__(self):
        self.e = None
        
        self.tableName__table = dict()
        
        self.conn = None
        
        self.batchOn    = False
        self.batchCount = 0
    
    
    def GetTableList(self):
        tableList = self.tableName__table.keys()
        tableList.sort()
        
        return tableList
        
    def GetTable(self, tableName):
        retVal = None
        
        if tableName in self.tableName__table:
            retVal = self.tableName__table[tableName]
        
        return retVal
    
    
    ######################################################################
    #
    # Private
    #
    ######################################################################
    
    @staticmethod
    def GetDatabaseRunningFullPath():
        dbDir      = SysDef.Get("CORE_DATABASE_RUNTIME_DIR", "/run/shm")
        user       = RunInfo().GetUser()
        dbFullPath = dbDir + "/" + user + "/database.db"
        
        return dbFullPath
    
    
    @staticmethod
    def GetDatabaseClosedFullPath():
        dbFullPath = CorePath("/runtime/db/database.db")
        
        return dbFullPath
        
    @staticmethod
    def GetDctConfigPath():
        return DirectoryPart(Database.GetDatabaseClosedFullPath()) + "/Dct.master.json"
    
    @staticmethod
    def GetDctCfg():
        return ConfigReader().ReadConfigOrAbort(Database.GetDctConfigPath())

        
    def Connect(self, createOnInit = False, verbose = False, forcedDbFullPath = None):
        retVal = True
        
        state = ServerState().GetState()
        
        dbFullPath = None
        if forcedDbFullPath:
            dbFullPath = forcedDbFullPath
        else:
            if state == "CLOSED":
                if FileExists(Database.GetDatabaseRunningFullPath()):
                    Log("Server CLOSED, but online database exists, selecting online database")
                    dbFullPath = Database.GetDatabaseRunningFullPath()
                else:
                    Log("Server CLOSED, selecting offline database")
                    dbFullPath = Database.GetDatabaseClosedFullPath()
            elif state == "STARTED":
                Log("Server STARTED, selecting online database")
                dbFullPath = Database.GetDatabaseRunningFullPath()
            else:
                Log("Server not CLOSED or STARTED, connection failed")
                retVal = False

        if retVal:
            Log("Connecting to database %s" % dbFullPath)
            self.conn             = sqlite3.connect(dbFullPath)
            self.conn.row_factory = sqlite3.Row
            
            retVal = self.Init(createOnInit, verbose)
        
        return retVal
    
    
    def Close(self):
        if self.conn:
            self.conn.close()
    
    
    
    # private
    def Init(self, createOnInit = True, verbose = False):
        retVal = True
        
        cfg = Database.GetDctCfg()
        
        dctTableList = cfg["tableList"]
        
        for dctTable in dctTableList:
            tableName = dctTable["name"]
            fieldList = dctTable["fieldList"]
            uniqueKeyFieldList = dctTable["uniqueKeyFieldList"]
            
            indexList = []
            if "indexList" in dctTable:
                indexList = dctTable["indexList"]
        
            if tableName in self.tableName__table:
                Log("Table % already defined" % tableName)
                retVal = False
                break

            else:
                if createOnInit:
                    Log("%s - Ensuring structure" % tableName)
                    self.CreateTable(tableName, fieldList, uniqueKeyFieldList, indexList)

                if verbose:
                    Log("%s - Internalizing structure" % tableName)
                    
                table = Table(self, tableName, fieldList, uniqueKeyFieldList, indexList)
                self.tableName__table[tableName] = table
                
        return retVal
        
        
    
    # Deal with concurrency exceptions
    # basically, if the database is locked doing some other process' work, then
    # exceptions can get thrown after a timeout goes off.
    # I am not interested in this, so simply re-try until something other than
    # a timeout exception occurs.
    def Execute(self, query, valList = [], allowFail = False):
        retVal = None
        
        if self.conn:
            c = self.conn.cursor()
            
            tryAgain = True
            
            while tryAgain:
                try:
                    c.execute(query, valList)
                    tryAgain = False
                except sqlite3.OperationalError as e:
                    if allowFail:
                        self.e = e
                        c = None
                        break
                    else:
                        time.sleep(0.050)
                except Exception as e:
                    raise e
            retVal = c
            
        return retVal
    
    
    def GetLastError(self):
        return self.e
        
    
    def CreateTableIndex(self, tableName, keyFieldList, unique = False):
        if len(keyFieldList):
            keyFieldListStr = ", ".join(keyFieldList)
            indexName       = "_".join(keyFieldList) + "_IDX"
            
            uniqueStr = ""
            if unique:
                uniqueStr = "UNIQUE"
            
            query = """
                CREATE %s INDEX IF NOT EXISTS %s
                ON %s ( %s )
                """ % (uniqueStr, indexName, tableName, keyFieldListStr)
                
            if not self.Execute(query, allowFail = True):
                Log("Create index fail: %s" % self.GetLastError())
                Log("Query: %s" % query)
                Log("Quitting")
                sys.exit(1)

    
    # http://www.sqlitetutorial.net/sqlite-autoincrement/
    # http://www.sqlitetutorial.net/sqlite-index/
    def CreateTable(self, tableName, fieldList, uniqueKeyFieldList = [], indexList = []):
        # 2-part setup
        #
        # Establish the shape of the table:
        # - all fields and types
        # - plus default adding TIMESTAMP field which is auto-set
        # - plus explicitly using rowid which never uses the same value twice
        #   - makes knowing last record seen very efficient, finding new too
        #
        # Then establish unique indexes, which guarantees that you can't get
        # duplicates if you try to insert another record with the same values.
        # This is used as a faster method of search-then-insert.
        #
        
        # Step 1, setup the shape of the table and create
        # Every field is a text field.
        # Generate a string which is <FIELD> text, <FIELD> text, <FIELD> text...
        
        schemaStr = ""
        sep = ""
        for field in fieldList:
            schemaStr += sep + "%s text" % field
            sep = ", "
        
        query = """
                CREATE TABLE IF NOT EXISTS %s
                (
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                    TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    %s
                )
                """ % (tableName, schemaStr)
        
        if not self.Execute(query, allowFail = True):
            Log("Create table fail: %s" % self.GetLastError())
            Log("Query: %s" % query)
            Log("Quitting")
            #sys.exit(1)
        
        # create timestamp index
        self.CreateTableIndex(tableName, ["TIMESTAMP"])
        
        # Step 2, establish the unique index
        self.CreateTableIndex(tableName, uniqueKeyFieldList, unique = True)
        
        # Step 3, create any table-specific indexes
        for indexFieldList in indexList:
            self.CreateTableIndex(tableName, indexFieldList)
    

    def Query(self, query, valList = []):
        retVal  = False
        rowList = []
        
        if self.conn:
            c = self.Execute(query, valList)
            rowList = c.fetchall()
            
            if len(rowList) != 0:
                retVal = True
        
        return retVal, rowList

    def BatchBegin(self):
        self.BatchEnd()
        
        self.batchOn = True
        
    def BatchEnd(self):
        retVal = self.batchCount
        
        if self.batchCount:
            self.conn.commit()
        
        self.batchOn    = False
        self.batchCount = 0
        
        return retVal
        
    def QueryCommit(self, query, valList = []):
        retVal = True
        
        try:
            self.Execute(query, valList)
        except:
            retVal = False
        
        if self.batchOn == False:
            self.conn.commit()
        else:
            self.batchCount += 1
        
        return retVal
        

        
        
        
        
        
from libEvm import *
        
        
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
        try:
            if msg["MESSAGE_TYPE"] == "DATABASE_STATE":
                state      = msg["STATE"]
                dbFullPath = msg["DATABASE_PATH"]
                
                if state == "DATABASE_AVAILABLE":
                    self.OnDatabaseAvailable(dbFullPath)
                elif state == "DATABASE_CLOSING":
                    self.OnDatabaseClosing()
        except Exception as e:
            Log("ERR: State connection message handler error: %s" % e)


    def OnClose(self, ws):
        Log("Connection lost to %s, exiting" % self.dbSvc)
        evm_MainLoopFinish()

        
    def OnError(self, ws):
        Log("Couldn't connect to %s, trying again" % (self.dbSvc))
    
    
    

class Table():
    def __init__(self, db, tableName, fieldList, keyFieldList = [], indexFieldListList = []):
        self.db                 = db
        self.tableName          = tableName
        self.fieldList          = fieldList
        self.keyFieldList       = keyFieldList
        self.indexFieldListList = indexFieldListList
        
        
    def GetFieldList(self):
        return self.fieldList
        
    def GetKeyFieldList(self):
        return self.keyFieldList
        
    def GetNonKeyFieldList(self):
        return [field for field in self.GetFieldList() if field not in self.GetKeyFieldList()]
    
    def GetRecordAccessor(self):
        return Record(self)
        
    def Count(self):
        retVal = 0
        
        query = """
                SELECT  count(*) as COUNT
                FROM    %s
                """ % (self.tableName)
    
        retVal, rowList = self.db.Query(query)
        
        if retVal:
            retVal = rowList[0]['COUNT']
        
        return retVal
    
    def GetHighestRowId(self):
        retVal = -1
        
        query = """
                SELECT    rowid
                FROM      %s
                ORDER BY  rowid DESC
                LIMIT     1
                """ % (self.tableName)
    
        retVal, rowList = self.db.Query(query)
        
        if retVal:
            retVal = int(rowList[0]['rowid'])
        
        return retVal
    
    def DeleteOlderThan(self, sec):
        countBefore = self.Count()
        
        query = """
                DELETE
                FROM    %s
                WHERE   TIMESTAMP <= datetime('now', '-%s seconds')
                """ % (self.tableName, sec)
    
        retVal = self.db.QueryCommit(query)
        
        countAfter = self.Count()
        
        retVal = countBefore - countAfter
        
        return retVal
        
    def Distinct(self, field):
        name__value = dict()
        
        query = """
                SELECT DISTINCT ( %s ) as %s, count(*) as COUNT
                FROM %s
                GROUP BY %s
                """ % (field, field, self.tableName, field)
        
        retVal, rowList = self.db.Query(query)
        
        if retVal:
            for row in rowList:
                name  = row[field]
                value = row["COUNT"]
                
                name__value[name] = value
            
        return name__value

        
class Record():
    def __init__(self, table, name__value = dict()):
        self.table = table
        
        self.Reset()
        self.Overwrite(name__value)
        
    def Reset(self):
        self.name__value = dict()
        
    ###############################
    ##
    ## Pretty
    ##
    ###############################
    
    def DumpVertical(self, printer = None):
        if printer == None:
            def Print(str):
                print(str)
            printer = Print
    
        printer(self.table.tableName + "[" + str(self.GetRowId()) + "]")
        
        max = 0
        for field in self.table.GetFieldList():
            strLen = len(field)
            
            if strLen > max:
                max = strLen
    
        formatStr = "  %-" + str(max) + "s: %s"

        for field in self.table.GetFieldList():
            printer(formatStr % (field, self.Get(field)))

    def DumpHorizontal(self, width = 8, printer = None):
        if printer == None:
            def Print(str):
                print(str)
            printer = Print
    
        
        dumpStr = "[" + str(self.GetRowId()) + "]"
        
        formatStr = "%-" + str(width) + "s"
        
        for field in self.table.GetFieldList():
            dumpStr += " "
            dumpStr += formatStr % (self.Get(field))

        printer(dumpStr)

    ###############################
    ##
    ## Convenience
    ##
    ###############################
    
    def GetDict(self):
        return self.name__value
    
    ###############################
    ##
    ## Field Accessors
    ##
    ###############################
    
    def GetRowId(self):
        rowid = self.Get('rowid')
        if rowid == "":
            rowid = -1
        
        return rowid
        
    def SetRowId(self, rowid):
        self.Set('rowid', rowid)
            
    def Get(self, name):
        retVal = ""

        if name in self.name__value:
            retVal = self.name__value[name]
        
        return retVal
    
    def Set(self, name, value):
        self.name__value[name] = value
    
    
    ###############################
    ##
    ## Database Operations
    ##
    ###############################
    
    def Read(self):
        retVal = False
        
        whereStr = ""
        sep = ""
        for keyField in self.table.keyFieldList:
            whereStr += sep + keyField + " = '" + self.Get(keyField) + "'"
            sep = " AND "
    
        query = """
                SELECT  rowid, datetime(TIMESTAMP, 'localtime') AS TIMESTAMP, *
                FROM    %s
                WHERE   %s
                """ % (self.table.tableName, whereStr)
    
        
        retVal, rowList = self.table.db.Query(query)
        
        if retVal:
            self.Overwrite(rowList[0])
        
        return retVal
    
    def Insert(self):
        retVal = False
        
        colNameListStr  = "( "
        colNameListStr += ", ".join(self.table.GetFieldList())
        colNameListStr += " )"
        
        valListStr = ""
        sep = ""
        for field in self.table.GetFieldList():
            valListStr += sep + "'" + self.Get(field) + "'"
            sep = ", "
        
        query = """
                INSERT INTO %s
                %s
                VALUES ( %s )
                """ % (self.table.tableName, colNameListStr, valListStr)
    
        retVal = self.table.db.QueryCommit(query)
        
        return retVal

        
    def ReadNextInLinearScan(self):
        query = """
                SELECT    rowid, datetime(TIMESTAMP, 'localtime') AS TIMESTAMP, *
                FROM      %s
                WHERE     rowid > %s
                ORDER BY  rowid ASC
                LIMIT     1
                """ % (self.table.tableName, self.GetRowId())
    
        retVal, rowList = self.table.db.Query(query)
        
        if retVal:
            self.Overwrite(rowList[0])

        return retVal
    
    
    def Delete(self):
        query = """
                DELETE
                FROM    %s
                WHERE   rowid = %s
                """ % (self.table.tableName, self.GetRowId())
    
        retVal = self.table.db.QueryCommit(query)
        
        return retVal
    
    def Update(self):
        updateStr = ""
        sep = ""
        for field in self.table.GetNonKeyFieldList():
            updateStr += sep + field + " = '" + self.Get(field) + "'"
            sep = ", "
    
        query = """
                UPDATE  %s
                SET     %s
                WHERE   rowid = %s
                """ % (self.table.tableName, updateStr, self.GetRowId())
    
        retVal = self.table.db.QueryCommit(query)
        
        return retVal
    
    
    
    
    
    ###############################
    ##
    ## Private
    ##
    ###############################
        
    def Overwrite(self, name__value):
        self.Reset()
        
        for key in name__value.keys():
            self.name__value[key] = name__value[key]
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
