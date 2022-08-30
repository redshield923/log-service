from calendar import c
import re
from signal import pause
import sqlite3
from .database import DatabaseHelper
from models.database import Index, LogResult, IndexResult
import json 

class LogHelper:
    
    databaseHelper: DatabaseHelper
    
    def __init__(self, databaseHelper: DatabaseHelper):
        self.databaseHelper = databaseHelper
        
    def index_if_exist(self, index: str):
        
        con, cur = self.databaseHelper.get_database_connection()
        
        find_index_sql = "SELECT * FROM log_index WHERE name = ?"
    
        cur.execute(find_index_sql, (index,))
        res: Index = cur.fetchone()
        print()
        print(res)
        con.close()
        if not res: 
            return False
        
        return res
    
    def create_index(self, index_name: str, user: int):
        
        con, cur = self.databaseHelper.get_database_connection()

        create_index_sql = "INSERT INTO log_index VALUES ( ?, julianday('now'), julianday('now'), ?)"
        cur.execute(create_index_sql, (index_name, user,))
        last_row_id = cur.lastrowid
        con.commit()
        cur.execute('SELECT * FROM log_index WHERE rowid = ?', (last_row_id,))
        inserted_row = cur.fetchone()
        con.commit()
        con.close()
        return inserted_row
        
    
    def create_if_not_exists(self, index_name: str, user_id: int):
        
        index = self.index_if_exist(index_name)
        
        if index: 
            return index
        
        return self.create_index(index_name, user_id)
 
    def ingest_log(self, index: str, source: str, payload):
        # insert a log
        # get§
        
        con, cur = self.databaseHelper.get_database_connection()
        
        create_new_log_sql = "INSERT INTO log (index_name, time_ingested, source) VALUES (?, julianday('now'), ?)"
        cur.execute(create_new_log_sql, (index, source))
        log_id = cur.lastrowid
        con.commit()
        
        # Parse json and insert a field for each key/value pair
        
        for k, v in payload.items():
            create_new_field_sql = "INSERT INTO field (log_id, name, payload) VALUES (?, ?, ?)"
            cur.execute(create_new_field_sql, (log_id, k, v))
            con.commit()
            
        con.close()
            

        return len(payload.items())
        
    def retrieve_index(self, index:str):
        
        
        get_logs_from_index_sql = """
            select f.name as field, f.payload as message, l.time_ingested as timestamp, l.source as source
            from field as f
            INNER JOIN log as l on f.log_id = l.id
            inner join log_index as i on i.name = l.index_name
            where i.name = ?
            """
            
        con, cur = self.databaseHelper.get_database_connection()
        
        cur.execute(get_logs_from_index_sql, (index,))
        
        res = cur.fetchall()
        
        if not res: 
            return False

        index_result: IndexResult = {'index_name': index, 'logs': [] }
        print(index_result['logs'])

        for row in res:
            
            formatted_row: LogResult = dict(row)
            
            index_result['logs'].append(formatted_row)
    
        
        return index_result