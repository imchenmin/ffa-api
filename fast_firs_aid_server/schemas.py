import datetime
from typing import Union
from pydantic import BaseModel
from fast_firs_aid_server.my_enum import GenderEnum


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


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


class AidItemCreate(AidItemBase):
    pass


class AidItem(AidItemBase):
    id: int
    initiator_id: int
    call_datetime: datetime.datetime
    # initiator: list[User] = []
    response_items: list[ResponseItem] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    phone_number: str
    real_name: str
    gender: GenderEnum


class UserCreate(UserBase):
    hashed_password: str


class User(UserBase):
    id: int
    aid_items: list[AidItem] = []
    disabled: Union[bool, None] = None

    class Config:
        orm_mode = True


class LocationItem(BaseModel):
    id: int
    user_id: int
    lon: float
    lat: float

    time_created: datetime.datetime



    class Config:
        orm_mode = True


class OtpCodeItem(BaseModel):
    """短信接收体
    需要控流
    """
    telephone: int


class OtpCodeReturnItem(BaseModel):
    """短信接收体
    需要控流
    """
    status: str
