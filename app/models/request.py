# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115, R0903

from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., description="The user of the requester")
    id: int = Field(..., description="The ID of the requester")
    active: int = Field(..., description="Wether the user is active or not")
    user_password: str = Field(...,
                               description="The plaintext password of the requester")
    time_created: datetime = Field(...,
                                   description="The time the user was created")
    time_updated: datetime = Field(...,
                                   description="The time the user was last updated")
    updated_by: str = Field(...,
                            description="The last admin to update the user")
    type: int = Field(..., description="The type ID of the user")


class LogPayload(BaseModel):
    index: str = Field(..., description="The index name")
    source: str = Field(..., description="The source of the index")
    payload: object = Field(
        ..., description="A JSON payload containing all fields wished to be ingested")


class IndexPatternPayload(BaseModel):
    index_pattern: str = Field(...,
                               description="The index pattern to search against")


class NewUser(BaseModel):
    username: str = Field(..., description="The username of the new user")
    user_password: str = Field(...,
                               description="The plaintext password of the new user")
    type: int = Field(..., description="The type of the new user")


class UpdatePassword(BaseModel):
    username: str = Field(..., description="The username to update against")
    password: str = Field(...,
                          description="The plaintext password to update with")
