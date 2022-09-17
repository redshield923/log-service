from datetime import datetime
from hashlib import sha256
from lib2to3.pytree import Base
from pickletools import string1
from pydantic import BaseModel


class User(BaseModel):
    username: str
    id: int
    active: int
    user_password: str
    time_created: datetime
    time_updated: datetime
    updated_by: str
    type: int


class LogPayload(BaseModel):
    index: str
    source: str
    payload: object


class IndexPatternPayload(BaseModel):
    index_pattern: str


class NewUser(BaseModel):
    username: str
    user_password: str
    type: int


class UpdatePassword(BaseModel):
    username: str
    password: str
