from datetime import datetime
from hashlib import sha256
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