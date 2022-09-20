import os


class Config:
    DATABASE_PATH = os.environ['LOGGING_DATABASE_PATH']
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    ALGORITHM = 'HS256'
    SECRET = os.environ['LOGGING_SECRET']
