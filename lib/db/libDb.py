import os
import sys

from libUtl import *
from libRun import *
from libSysDef import *
from libServerState import *

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
        tableList = sorted(self.tableName__table.keys())
        
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
        dbDir      = SysDef.Get("CORE_DATABASE_RUNTIME_DIR")
        user       = RunInfo().GetUser()
        dbFullPath = dbDir + "/" + user + "/database.db"
        
        return dbFullPath
    
    
    @staticmethod
    def GetDatabaseClosedFullPath():
        dbFullPath = CorePath("/runtime/db/database.db")
        
        return dbFullPath
        
    @staticmethod
    def GetDatabaseBackupFullPath():
        dbFullPath = CorePath("/runtime/db/database.db.bak")
        
        return dbFullPath
        
    @staticmethod
    def GetDctConfigPath():
        return DirectoryPart(Database.GetDatabaseClosedFullPath()) + "/Dct.master.json"
    
    
    @staticmethod
    def DoRunningBackup():
        backupWorked = Database.DoBackup(Database.GetDatabaseRunningFullPath(),
                                         Database.GetDatabaseBackupFullPath())
        
        if backupWorked:
            Log("Overwriting offline database with backup")
            copyWorked = SafeCopyFileIfExists(Database.GetDatabaseBackupFullPath(),
                                              Database.GetDatabaseClosedFullPath())
            if copyWorked:
                Log("  Success")
            else:
                Log("  Fail")
        else:
            pass
            
        SafeRemoveFileIfExists(Database.GetDatabaseBackupFullPath())
        
    
    @staticmethod
    def DoBackup(dbFrom, dbTo):
        retVal = True
        
        Log("Backing up from %s to %s" % (dbFrom, dbTo))
        
        try:
            timeStart = DateTimeNow()
            subprocess.check_output(["sqlite3", dbFrom, ".timeout 10000", ".backup %s" % dbTo])
            timeEnd = DateTimeNow()
            secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
            
            Log("Backup complete, took %s sec" % secDiff)
        except Exception as e:
            Log("Backup failed: %s" % e)
            retVal = False
        
        return retVal
    
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
            if FileExists(Database.GetDatabaseRunningFullPath()):
                if state == "STARTED":
                    dbFullPath = Database.GetDatabaseRunningFullPath()
                else:
                    Log("Connection failed: Online DB exists but state not STARTED")
                    retVal = False
            elif FileExists(Database.GetDatabaseClosedFullPath()):
                if state == "CLOSED":
                    dbFullPath = Database.GetDatabaseClosedFullPath()
                else:
                    Log("Connection failed: Offline DB exists but state not CLOSED")
                    retVal = False
            else:
                Log("Connection failed: No Online/Offline DB instances found")
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
                    if str(e) == "disk I/O error":
                        Log("Database gone, aborting")
                        sys.exit(1)
                    
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
            indexName       = "_".join(keyFieldList) + "_IDX_" + tableName
            
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
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
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
        except sqlite3.IntegrityError:
            retVal = False
        
        if self.batchOn == False:
            self.conn.commit()
        else:
            self.batchCount += 1
        
        return retVal
        


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
        name__value = dict()
        for field in self.GetFieldList():
            name__value[field] = ""

        return Record(self, name__value)
        
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
                SELECT    ID as rowid
                FROM      %s
                ORDER BY  rowid DESC
                LIMIT     1
                """ % (self.tableName)

        retVal, rowList = self.db.Query(query)
        
        if retVal:
            retVal = int(rowList[0]['rowid'])
        
        return retVal
    
    def DeleteOlderThanInternal(self, sec):
        countBefore = self.Count()
        
        query = """
                DELETE
                FROM    %s
                WHERE   TIMESTAMP <= datetime('now', '-%s seconds')
                LIMIT   1000
                """ % (self.tableName, sec)
    
        retVal = self.db.QueryCommit(query)
        
        countAfter = self.Count()
        
        retVal = countBefore - countAfter
        
        return retVal

    def DeleteOlderThan(self, sec):
        retVal = 0

        count = self.DeleteOlderThanInternal(sec)
        retVal += count
        
        while count:
            count = self.DeleteOlderThanInternal(sec)
            retVal += count

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
                SELECT  ID as rowid, datetime(TIMESTAMP, 'localtime') AS TIMESTAMP, *
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
                SELECT    ID as rowid, datetime(TIMESTAMP, 'localtime') AS TIMESTAMP, *
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
                WHERE   ID = %s
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
                WHERE   ID = %s
                """ % (self.table.tableName, updateStr, self.GetRowId())
    
        retVal = self.table.db.QueryCommit(query)
        
        return retVal
    
    
    
    # copies fields from another record, even from another table.
    # does not clear its own values first.
    # copies only fields it currently has which overlap with second record
    def CopyIntersection(self, rec):
        name__value = rec.GetDict()

        self.CopyDictIntersection(name__value)

    def CopyDictIntersection(self, name__value):
        for key in self.name__value.keys():
            if key in name__value:
                self.name__value[key] = str(name__value[key])
    
    
    ###############################
    ##
    ## Private
    ##
    ###############################
        
    # clears itself first, then copies in values
    def Overwrite(self, name__value):
        self.Reset()
        
        for key in name__value.keys():
            self.name__value[key] = name__value[key]
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
