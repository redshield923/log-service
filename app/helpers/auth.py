import sys
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Union
from .database import DatabaseHelper
from models.auth import TokenData
from models.database import User
from jose import jwt, JWTError
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthHelper:

    secret: str
    algorithm: str
    databaseHelper: DatabaseHelper

    def __init__(self, secret: str, algorithm: str, databaseHelper: DatabaseHelper):

        self.secret = secret
        self.algorithm = algorithm
        self.databaseHelper = databaseHelper

    def get_user(self, username: str):
        find_user_sql = "SELECT * FROM user WHERE username = ?"
        con, cur = self.databaseHelper.get_database_connection()
        cur.execute(find_user_sql, [username])
        user_response = cur.fetchall()

        print(user_response)
        if len(user_response) == 0:
            return None

        user_dict: User = dict(user_response[0])
        con.close()

        return User(**user_dict)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user:
            return False
        if not self.correct_password(user.password, password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.secret, algorithm=self.algorithm)
        return encoded_jwt

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret,
                                 algorithms=[self.algorithm])
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

    def correct_password(self, password_hash: str, password: str):

        return True if password_hash == sha256(password.encode('utf-8')).hexdigest() else False
