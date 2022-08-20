from pydantic import BaseModel, Field

class Health(BaseModel):
    '''Schema for return of the health function'''
    app_health: bool = Field(..., description="The health of the app")
    db_health: bool = Field(..., description="The health of the database")
    hostname: str = Field(..., description="The name of the current host")
    
    