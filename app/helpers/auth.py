# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115


from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from password_strength import PasswordPolicy
from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from models.auth import TokenData
from models.database import User
from .database import DatabaseHelper

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

password_policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
    # need min. 1 non-letter characters (digits, specials, anything)
    nonletters=1,
)


class AuthHelper:

    secret: str
    algorithm: str
    databaseHelper: DatabaseHelper

    def __init__(self, secret: str, algorithm: str, database_helper: DatabaseHelper):

        self.secret = secret
        self.algorithm = algorithm

        # pylint: disable=C0103
        self.databaseHelper = database_helper

    def validate_password_strength(self, password: str):
        breaches = password_policy.test(password)

        return len(breaches) == 0

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
        except JWTError as exc:
            raise credentials_exception from exc
        user = self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    def correct_password(self, password_hash: str, password: str):
        password_hasher = PasswordHasher()
        try:
            password_hasher.verify(password_hash, password)
        except VerificationError:
            return False

        return True

    def hash_password(self, password: str):
        password_hasher = PasswordHasher()
        return password_hasher.hash(password.encode('utf-8'))
