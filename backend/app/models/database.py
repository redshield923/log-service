from sqlite3 import Date
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
    id: int
    name: str
    time_created: Date
    time_updated: Date
    updated_by: int