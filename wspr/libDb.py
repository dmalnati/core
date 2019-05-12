import sqlite3


class Database():
    def __init__(self, databaseName):
        self.databaseName = databaseName
        
        self.conn = sqlite3.connect(self.databaseName)
        
        self.conn.row_factory = sqlite3.Row
        
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
        schemaStr = ", ".join(" ".join(list(x)) for x in schema)
        
        # handle creating TIMESTAMP field, which isn't part of the key
        # unless input indicates it as such
        timestampFieldStr = "TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, "
        
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
        print(query)

        c = self.conn.cursor()
        c.execute(query)
    

    def Query(self, query, valList = []):
        retVal = False
        
        print(query)
        
        self.c = self.conn.cursor()
        self.c.execute(query, valList)
        self.all = self.c.fetchall()
        
        if len(self.all) != 0:
            retVal = True
        
        return retVal



    def QueryCommit(self, query, valList = []):
        print(query)
        
        c = self.conn.cursor()
        c.execute(query, valList)
        self.conn.commit()
        
        return True
        
    
    def GetNext(self, rec):
        retVal = False
        
        if len(self.all):
            retVal = True
            
            row      = self.all[0]
            self.all = self.all[1:]
            
            for key in row.keys():
                rec.Set(key, row[key])
        
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
    
    def GetRecordAccessor(self):
        return Record(self)

        
class Record():
    def __init__(self, table, name__value = dict()):
        self.table       = table
        self.name__value = name__value
        
    def Reset(self):
        for key in self.name__value.keys():
            self.Set(key, "")

    def Get(self, name):
        retVal = ""

        retVal = self.name__value[name]
        
        return retVal
    
    def Set(self, name, value):
        self.name__value[name] = value
    
    
    def RecordExistsInDatabase(self):
        retVal = False
        
        whereStr = ""
        sep = ""
        for keyField in self.table.keyFieldList:
            whereStr += sep + keyField + " = '" + self.Get(keyField) + "'"
            sep = " AND "
    
        query = """
                SELECT  *
                FROM    %s
                WHERE   %s
                """ % (self.table.tableName, whereStr)
    
        retVal = self.table.db.Query(query)
        
        print("retVal: %s" % retVal)

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
        
        print("retVal: %s" % retVal)

        return retVal

        
    def StartLinearScan(self):
        query = """
                SELECT  *
                FROM    %s
                ORDER BY rowid
                """ % (self.table.tableName)
    
        retVal = self.table.db.Query(query)
        
        print("retVal: %s" % retVal)

        return retVal
        
    def GetNext(self):
        return self.table.db.GetNext(self)
        
        
        
        
        