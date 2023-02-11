# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115, R0903

from pydantic import BaseModel, Field


class Health(BaseModel):
    '''Schema for return of the health function'''
    app_health: bool = Field(..., description="The health of the app")
    db_health: bool = Field(..., description="The health of the database")
    hostname: str = Field(..., description="The name of the current host")


class Token(BaseModel):
    access_token: str = Field(..., description="The access token")
    token_type: str = Field(..., description="The type of token")
