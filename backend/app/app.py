import socket
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

class App:
    
    def __init__(self, version: str, database_path: str):
        self.app: object = FastAPI(version=version)
        self.database_path: str = database_path
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
    
        @self.app.get('/')       
        def __route_index():
            return self.index()
        
        @self.app.get('/health')
        def __route_health():
            return self.health()
    
        
    def get_app(self):
        return self.app
        
    def index(self):
        return {"Status": 200}
    
    def health(self):
        hostname: str = socket.gethostname()
        res = { "status": 200, "body": {"database_status": 200, "app_status": 200, "hostname": hostname } }
        
        print(f'connecting to database file ${self.database_path}')
        con = sqlite3.connect(self.database_path)
        
        try:
            cur = con.cursor()
            cur.execute('''create table test (test int)''')
            cur.execute('''insert into test values (1)''')
            cur.execute('''select * from test''')
            cur.execute('''drop table test''')
        except Exception:
            con.commit()
            con.close()
            
            database_health = False
            
        if(database_health):
            res["body"]["database_status"] = 500

        return res        
        
        
        