# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115, R0903

import secrets
import os


class Config:
    DATABASE_PATH: str

    try:
        DATABASE_PATH = os.environ['LOGGING_DATABASE_PATH']
    except KeyError:
        DATABASE_PATH = '/code/app/database/sqlite.db'

    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    ALGORITHM = 'HS256'

    try:
        SECRET = os.environ['LOGGING_SECRET']
    except KeyError:
        SECRET = secrets.token_hex(32)
