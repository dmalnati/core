import sqlite3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


class Database():
    def __init__(self, databaseName):
        self.databaseName = databaseName
        
        self.conn = sqlite3.connect(self.databaseName)
        
        self.conn.row_factory = sqlite3.Row
        
        self.batchOn    = False
        self.batchCount = 0
        
    def GetFieldListFromSchema(self, schema):
        return [x[0] for x in schema]

    
    def TableExists(self, table):
        retVal = False
        
        valList = [(table)]
        
        query = """
                SELECT  name
                FROM    sqlite_master
                WHERE   type='table' AND name=?
                """
        
        c = self.conn.cursor()
        c.execute(query, valList)
        
        if c.fetchone() != None:
            retVal = True
        
        return retVal
        
    def CreateTable(self, name, schema, keyFieldList = []):
        # handle creating TIMESTAMP field, which isn't part of the key
        # unless input indicates it as such
        timestampFieldStr = "TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, "
        
        schemaStr = ", ".join(" ".join(list(x)) for x in schema)
        
        # handle creating primary key
        keyStr = ""
        if len(keyFieldList):
            keyStr += ", PRIMARY KEY("
            keyStr += ", ".join(keyFieldList)
            keyStr += ")"
        
        query = """
                CREATE TABLE %s
                ( %s %s %s )
                """ % (name, timestampFieldStr, schemaStr, keyStr)

        c = self.conn.cursor()
        c.execute(query)
    

    def Query(self, query, valList = []):
        retVal  = False
        rowList = []
        
        c = self.conn.cursor()
        c.execute(query, valList)
        
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
        
        c = self.conn.cursor()
        
        try:
            c.execute(query, valList)
        except:
            retVal = False
        
        if self.batchOn == False:
            self.conn.commit()
        else:
            self.batchCount += 1
        
        return retVal
        
    
    

class Table():
    def __init__(self, db, tableName, schema, keyFieldList = []):
        self.db           = db
        self.tableName    = tableName
        self.schema       = schema
        self.keyFieldList = keyFieldList
        
        if self.db.TableExists(self.tableName) == False:
            self.db.CreateTable(self.tableName, self.schema, keyFieldList)
        
    def GetFieldList(self):
        return self.db.GetFieldListFromSchema(self.schema)
        
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        