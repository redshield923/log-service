import socket, sqlite3
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from models import response
from models import request
from models.database import User
from helpers.auth import AuthHelper
from helpers.database import DatabaseHelper
from config import Config

app: FastAPI = FastAPI(version='0.0.1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

databaseHelper = DatabaseHelper(Config.database_path)
authHelper = AuthHelper(Config.SECRET, Config.ALGORITHM, databaseHelper)

@app.get('/')     
def index():
    return {"Hello": "World"}

@app.get('/health', response_model=response.Health)
def health(current_user: User = Depends( authHelper.get_current_user)):
    hostname: str = socket.gethostname()
    res = { "db_health": True, "app_health": True, "hostname": hostname } 
    database_health = True
    print(f'connecting to database file ${ database_path}')
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

# @app.post('/index/{index}')
# def index(index: str, current_user: request.User = Depends( authHelper.get_current_user)):
#     return   authHelper.ingest_log(index)
