from datetime import datetime
from hashlib import sha256

class User():
    user_id: int
    username: str
    active: int
    password_hash: str
    active: int
    time_created: datetime
    time_updated: datetime
    updated_by: str
    
    def __init__(self, user: object):
            self.username = user['username'] 
            self.user_id = user['id']
            self.password_hash = user['user_password']
            self.active = user['active']
            self.time_created = user['time_created']
            self.time_updated = user['time_updated']
            self.updated_by = user['updated_by']
            
    def correct_password(self, password: str):
        
        given_password_hash = sha256(password.encode('utf-8')).hexdigest()
        
        if self.password_hash == given_password_hash:
            return True
        
        return True if self.password_hash == given_password_hash else False
        
        
    
    