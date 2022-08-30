import socket, sqlite3
import os
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from models.database import Index
from models import response
from models import request
from models.database import User
from helpers.auth import AuthHelper
from helpers.database import DatabaseHelper
from helpers.log import LogHelper
from config import Config

app = FastAPI(version='0.0.1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

databaseHelper = DatabaseHelper(Config.database_path)
authHelper = AuthHelper(Config.SECRET, Config.ALGORITHM, databaseHelper)
logHelper = LogHelper(databaseHelper)

@app.get('/')     
def index():
    return {"Hello": "World"}

@app.get('/health', response_model=response.Health)
def health(current_user: User = Depends( authHelper.get_current_user)):
    hostname: str = socket.gethostname()
    res = { "db_health": True, "app_health": True, "hostname": hostname } 
    database_health = True
    print(f'connecting to database file ${Config.database_path}')
    con, cur =  databaseHelper.get_database_connection()
    
    try:
        cur.execute('''create table test (test int)''')
        cur.execute('''insert into test values (1)''')
        cur.execute('''select * from test''')
        cur.execute('''drop table test''')
    except sqlite3.Error:
        con.commit()
        con.close()
        
        database_health = False
        
    if(database_health):
        res["body"]["database_status"] = 500

    return res        
        
@app.post('/token')
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    user: User =   authHelper.authenticate_user(form_data.username, form_data.password)
    if not user: 
        raise HTTPException(status_code=401, detail="Incorrect Username or Password")
    
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token =   authHelper.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/user/me')
def get_current_user(current_user: request.User = Depends(authHelper.get_current_user)):
    return current_user

@app.post('/ingest/')
def index(payload: request.LogPayload, current_user: request.User = Depends( authHelper.get_current_user)):
    
    print(payload.payload)
    index: Index = logHelper.create_if_not_exists(payload.index, current_user.id)
    
    fields_unpacked = logHelper.ingest_log(index=payload.index, source=payload.source, payload=payload.payload)
    
    return {'success': True, 'fields_unpacked': fields_unpacked}
    
@app.get("/logs/{index}")
def get_logs(index: str, current_user: request.User = Depends( authHelper.get_current_user)):
    
    
    return logHelper.retrieve_index(index)