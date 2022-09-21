from datetime import datetime
from sqlite3 import Date
from typing import List
from pydantic import BaseModel


class UserType(BaseModel):
    id: int
    type: str


class User(BaseModel):
    id: int
    username: str
    password: str
    time_created: Date
    time_updated: Date
    updated_by: str
    type: int


class Index(BaseModel):
    name: str
    time_created: Date
    time_updated: Date
    updated_by: int


class LogResult(BaseModel):
    id: int
    index_name: str
    field: str
    messaage: str
    timestamp: datetime
    source: str


class IndexResult(BaseModel):
    index_name: str
    logs: List[LogResult]
