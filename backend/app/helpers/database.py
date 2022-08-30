    
import sqlite3


class DatabaseHelper:
    
    database_path: str    
    def __init__(self, database_path: str):
        self.database_path = database_path

    def get_database_connection(self):
        con = sqlite3.connect(self.database_path)
        con.row_factory = sqlite3.Row  
        cur = con.cursor()
        
        return con, cur
    
    