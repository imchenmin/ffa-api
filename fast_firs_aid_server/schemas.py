import datetime
from typing import Union
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    phone_number: str
    real_name: str


class UserCreate(UserBase):
    hashed_password: str


class User(UserBase):
    id: int
    items: list[Item] = []
    disabled: Union[bool, None] = None

    class Config:
        orm_mode = True


class ResponseBase(BaseModel):
    description: int
    owner_id: int
    aid_item_id: int

    response_state: int
    response_datetime: datetime.datetime


class ResponseItem(ResponseBase):
    id: int

    class Config:
        orm_mode = True


class AidItemBase(BaseModel):
    aid_type: str
    description: Union[str, None] = None
    call_datetime: datetime.datetime


class AidItemCreate(AidItemBase):
    pass


class AidItem(AidItemBase):
    id: int
    initiator_id: int
    # initiator: list[User] = []
    response_items: list[ResponseItem] = []

    class Config:
        orm_mode = True
