from hashlib import sha256
import re
import socket
import sqlite3
from datetime import timedelta
from turtle import st
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from .models.database import Index
from .models import response
from .models import request
from .models.database import User
from .helpers.auth import AuthHelper
from .helpers.database import DatabaseHelper
from .helpers.log import LogHelper
from .helpers.user import UserHelper
from .config import Config

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="app/templates")


app = FastAPI(version='0.0.1')
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

databaseHelper = DatabaseHelper(Config.database_path)
authHelper = AuthHelper(Config.SECRET, Config.ALGORITHM, databaseHelper)
logHelper = LogHelper(databaseHelper)
userHelper = UserHelper(databaseHelper)


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/health', response_model=response.Health)
def health(current_user: User = Depends(authHelper.get_current_user)):
    hostname: str = socket.gethostname()
    res = {"db_health": True, "app_health": True, "hostname": hostname}
    database_health = True
    print(f'connecting to database file ${Config.database_path}')
    con, cur = databaseHelper.get_database_connection()

    try:
        cur.execute('''create table test (test int)''')
        cur.execute('''insert into test values (1)''')
        cur.execute('''select * from test''')
        cur.execute('''drop table test''')
    except sqlite3.Error:
        con.commit()
        con.close()

        database_health = False

    if (database_health):
        res["body"]["database_status"] = 500

    return res


@app.post('/token', status_code=200)
def token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    user: User = authHelper.authenticate_user(
        form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect Username or Password")

    access_token_expires = timedelta(
        minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authHelper.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.status_code = status.HTTP_200_OK
    response.set_cookie('LOGGING_SERVICE_TOKEN', access_token,
                        httponly=True, secure=True, samesite='none')
    return {"access_token": access_token, "token_type": "bearer", 'access_token_expires': access_token_expires}


@app.get('/user/me')
def get_current_user(current_user: request.User = Depends(authHelper.get_current_user)):
    return current_user


@app.post('/ingest/')
def index(payload: request.LogPayload, current_user: request.User = Depends(authHelper.get_current_user)):

    print(payload.payload)
    index: Index = logHelper.create_if_not_exists(
        payload.index, current_user.id)

    fields_unpacked = logHelper.ingest_log(
        index=payload.index, source=payload.source, payload=payload.payload)

    return {'success': True, 'fields_unpacked': fields_unpacked}


@app.get("/index/{index}")
def get_logs(index: str, current_user: request.User = Depends(authHelper.get_current_user)):
    return logHelper.retrieve_index(index)


@app.get("/index/")
def get_logs(current_user: request.User = Depends(authHelper.get_current_user)):
    return logHelper.retrieve_all_indexes()


def validate_index_pattern(index_pattern: str):

    error: HTTPException = None

    if '*' not in index_pattern:
        error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail="Index Pattern must contain asterisk")

    if index_pattern.count('*') == 1 and not (index_pattern.startswith('*') or index_pattern.endswith('*')):
        error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail="If two wildcards are supplied, they must be at the start and end.")

    if index_pattern.count('*') == 2 and not (index_pattern.startswith('*') and index_pattern.endswith('*')):
        error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail="If two wildcards are supplied, they must be at the start and end.")
    if index_pattern.count('*') > 2:
        error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                              detail="Index Pattern must contain no more than two asterisk")

    return index_pattern.replace('*', '%'), error


@app.post("/search/")
def get_logs(request: request.IndexPatternPayload, current_user: request.User = Depends(authHelper.get_current_user)):

    search_term, error = validate_index_pattern(request.index_pattern)

    print(search_term)

    if error:
        return error

    return logHelper.retrieve_index_by_pattern(search_term)


@app.delete("/index/{index}")
def delete_index(index: str, current_user: request.User = Depends(authHelper.get_current_user)):

    # Only admins can delete indexes.
    if current_user.type == 1:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action.")

    if not logHelper.index_if_exist(index=index):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Index not found.")

    logHelper.delete_index(index)

    return status.HTTP_204_NO_CONTENT


# User actions

@app.post("/user")
def create_user(request: request.NewUser, current_user: request.User = Depends(authHelper.get_current_user)):

    # Only admins can create new users.
    if current_user.type == 1:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action.")

    success = userHelper.create_new_users(
        request.username, sha256(request.user_password.encode('utf-8')).hexdigest(), current_user.id, request.type)

    if success:
        return {"success": True}

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An error occured whilst creating a new user. This username may already exist.")


@app.put('/password')
def update_password(request: request.UpdatePassword, current_user: request.User = Depends(authHelper.get_current_user)):

    # Only admins can create new users.
    if current_user.type == 1:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action.")

    success = userHelper.update_password(
        request.username, sha256(request.password.encode('utf-8')).hexdigest())

    if success:
        return {"success": True}

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An error occured whilst updating user password. This username may already exist.")
