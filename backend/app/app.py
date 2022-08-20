from datetime import timedelta
from distutils.spawn import find_executable
from typing import Union
from datetime import datetime
from jose import JWTError, jwt
import socket
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import sqlite3
from models import response
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class App:
    
    app: object
    database_path: str
    oauth2_scheme: object
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET: str
    ALGORITHM: str
    
    def __init__(self, version: str, database_path: str,secret: str, access_token_expires_minutes: int = 60, algorithm: str = 'HS256'):
        self.app: object = FastAPI(version=version)
        self.database_path: str = database_path
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = access_token_expires_minutes
        self.ALGORITHM = algorithm
        self.SECRET = secret
        
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
        
        @self.app.get('/health', response_model=response.Health)
        def __route_health():
            return self.health()
        
        @self.app.post('/token')
        async def __route_token(form_data: OAuth2PasswordRequestForm = Depends()):
            return self.login_for_access_token(form_data)
        
        @self.app.get('/user/me')
        async def __route_get_current_user(current_user: User = Depends(self.get_current_active_user)):
            return current_user
    
        
    def get_app(self):
        return self.app
        
    def index(self):
        return {"Hello": "World"}
    
    def health(self):
        hostname: str = socket.gethostname()
        res = { "db_health": True, "app_health": True, "hostname": hostname } 
        
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
        
    def token(self, token: str):
        return {"token": token}
        
    def get_user(self, username: str):
        
        find_user_sql = f"SELECT * FROM user WHERE username = '{username}'"
        print(find_user_sql)
        con = sqlite3.connect(self.database_path)
        con.row_factory = sqlite3.Row  
        cur = con.cursor()
        cur.execute(find_user_sql)
        user_response = cur.fetchall()
        user_dict = dict(user_response[0])
        con.close()
        print(user_dict['username'], type(user_dict['username']))
        
        if user_response is None: 
            return None
        
        return User(user_dict)
                
    def authenticate_user(self, username: str, password: str):
        
        user = self.get_user(username)
        if not user:
            return False
        if not user.correct_password(password=password):
            return False
        return user 
    
    def login_for_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()):
        user = self.authenticate_user(form_data.username, form_data.password)
        
        if not user: 
            raise HTTPException(status_code=401, detail="Incorrect Username or Password")
        
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    
    async def get_current_active_user(current_user: User = Depends(get_current_user)):
        if not current_user.active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user


