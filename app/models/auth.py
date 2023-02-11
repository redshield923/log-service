# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115, R0903

from typing import Union
from pydantic import BaseModel


class TokenData(BaseModel):
    username: Union[str, None] = None
