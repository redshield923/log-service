from typing import Union
from pydantic import BaseModel


class TokenData(BaseModel):
    username: Union[str, None] = None
