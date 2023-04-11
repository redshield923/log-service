# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115

import socket
import sqlite3
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from utils import validate_index_pattern
from models import response
from models import request
from models.database import User
from helpers.auth import AuthHelper
from helpers.database import DatabaseHelper
from helpers.log import LogHelper
from helpers.user import UserHelper
from config.config import Config

templates = Jinja2Templates(directory="templates")

app = FastAPI(version='0.0.1')

# Mount static directory for html files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add middleware and CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

# Add rate-limiting config
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

databaseHelper = DatabaseHelper(Config.DATABASE_PATH)
authHelper = AuthHelper(Config.SECRET, Config.ALGORITHM, databaseHelper)
logHelper = LogHelper(databaseHelper)
userHelper = UserHelper(databaseHelper)


@app.get('/')
@limiter.limit("10/minute")
def index(request: Request):  # pylint: disable=W0621
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/health', response_model=response.Health)
def health(current_user: User = Depends(authHelper.get_current_user)):

    if not current_user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    hostname: str = socket.gethostname()
    res = {"db_health": True, "app_health": True, "hostname": hostname}
    print(f'connecting to database file ${Config.DATABASE_PATH}')
    con, cur = databaseHelper.get_database_connection()

    try:
        cur.execute('''create table test (test int)''')
        con.commit()
        cur.execute('''insert into test values (1)''')
        con.commit()
        cur.execute('''select * from test''')
        cur.execute('''drop table test''')
    except sqlite3.Error as err:
        con.commit()
        con.close()
        print(err)
        res['db_health'] = False

    con.close()
    return res


@app.post('/token', status_code=200)
@limiter.limit("10/minute")
def token(login_data: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    user: User = authHelper.authenticate_user(
        form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect Username or Password")

    access_token_expires = timedelta(
        minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # pylint: disable=E1101
    access_token = authHelper.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    login_data.status_code = status.HTTP_200_OK
    login_data.set_cookie('LOGGING_SERVICE_TOKEN', access_token,
                          httponly=True, secure=True, samesite='none')
    return {"access_token": access_token, "token_type": "bearer",
            'access_token_expires': access_token_expires}


@app.get('/user/me')
@limiter.limit("10/minute")
def get_current_user(current_user: request.User = Depends(authHelper.get_current_user)):
    return current_user


@app.post('/ingest/')
@limiter.limit("10/minute")
def ingest_log(payload: request.LogPayload,
               current_user: request.User = Depends(authHelper.get_current_user)):

    logHelper.create_if_not_exists(
        payload.index, current_user.id)

    fields_unpacked = logHelper.ingest_log(
        index=payload.index, source=payload.source, payload=payload.payload)

    return {'success': True, 'fields_unpacked': fields_unpacked}


@app.get("/index/{index}")
@limiter.limit("10/minute")
def get_logs(index_name: str, current_user: request.User = Depends(authHelper.get_current_user)):

    if not current_user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    res = logHelper.retrieve_index(index_name)

    if not res:

        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="No logs exist under this index yet! Hit /ingest to fix that!")

    return res


@app.get("/index/")
@limiter.limit("10/minute")
def get_all_indexes(current_user: request.User = Depends(authHelper.get_current_user)):

    if not current_user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    results = logHelper.retrieve_all_indexes()
    if not results:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No indexes found")

    return results


@app.post("/search/")
@limiter.limit("10/minute")
def get_logs_from_pattern(req: request.IndexPatternPayload,
                          current_user: request.User = Depends(authHelper.get_current_user)):

    if not current_user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    search_term, error = validate_index_pattern(req.index_pattern)

    print(search_term)

    if error:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=error)
    results = logHelper.retrieve_index_by_pattern(search_term)
    if not results:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No indexes found")

    return results


@app.delete("/index/{index}")
@limiter.limit("10/minute")
def delete_index(index_name: str,
                 current_user: request.User = Depends(authHelper.get_current_user)):

    # Only admins can delete indexes.
    if current_user.type == 1:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Not authorized to perform this action.")

    if not logHelper.get_index(index_name):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Index not found.")

    logHelper.delete_index(index_name)

    return status.HTTP_204_NO_CONTENT


# User actions

@app.post("/user")
@limiter.limit("10/minute")
def create_user(req: request.NewUser, current_user:
                request.User = Depends(authHelper.get_current_user)):

    # Only admins can create new users.
    if current_user.type == 1:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Not authorized to perform this action.")

    if not authHelper.validate_password_strength(req.user_password):
        return HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                             detail="""Password must contain one of each:
                             uppercase letter, lowercase letter, number, special character,
                             and be at least 8 characters in length.""")

    password_sha256 = authHelper.hash_password(req.user_password)
    success = userHelper.create_new_user(
        req.username, password_sha256, current_user.id, req.type)

    if success:
        return {"success": True}

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="An error occured whilst creating a new user.")


@app.put('/password')
@limiter.limit("10/minute")
def update_password(req: request.UpdatePassword,
                    current_user: request.User = Depends(authHelper.get_current_user)):

    # Only admins can reset passwords.
    if current_user.type == 1:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Not authorized to perform this action.")

    password_sha256 = authHelper.hash_password(req.password)
    success = userHelper.update_password(req.username, password_sha256)

    if success:
        return {"success": True}

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="An error occured whilst updating user password.")


@app.delete('/user/{username}')
@limiter.limit("10/minute")
def delete_user(username: str, current_user: request.User = Depends(authHelper.get_current_user)):

    # Only admins can delete users.
    if current_user.type == 1:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Not authorized to perform this action.")

    success = userHelper.delete_user(
        username)

    if success:
        return {"success": True}

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="An error occured whilst deleting user.")
