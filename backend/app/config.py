import os


class Config:
    database_path = os.environ['LOGGING_DATABASE_PATH']
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    ALGORITHM = 'HS256'
    SECRET = os.environ['LOGGING_SECRET']
