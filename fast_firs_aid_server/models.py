import datetime
import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, func, Enum
from sqlalchemy.orm import relationship
from fast_firs_aid_server.database import Base
from fast_firs_aid_server.my_enum import GenderEnum


class User(Base):
    """
    用户数据库模型类
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String, unique=True, index=True)
    real_name = Column(String, index=True)
    disabled = Column(Boolean, default=False)
    gender = Column(Enum(GenderEnum), default=GenderEnum.male)

    responses = relationship("ResponseItem", back_populates="owner")
    aid_items = relationship("AidItem", backref="users")


"""
响应事件数据库模型类
"""


class ResponseItem(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))  # 谁响应，是谁
    aid_item_id = Column(Integer, ForeignKey("aid_items.id"))
    response_state = Column(Integer, index=True)  # TODO 赋予实际意义
    response_datetime = Column(DateTime, index=True, default=datetime.datetime.utcnow())

    aid_item = relationship("AidItem", back_populates="response_items")
    owner = relationship("User", back_populates="responses")


"""
急救事件数据库模型类
"""


class AidItem(Base):
    __tablename__ = "aid_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    aid_type = Column(String, index=True)
    description = Column(String, index=True)
    call_datetime = Column(DateTime, index=True, default=datetime.datetime.utcnow())

    initiator_id = Column(Integer, ForeignKey("users.id"))
    # initiator = relationship("User", back_populates="aid_items")
    response_items = relationship("ResponseItem", back_populates="aid_item")


class LocationItem(Base):
    """
    权宜数据表示
    """
    __tablename__ = "location_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    lon = Column(Float, index=True)
    lat = Column(Float, index=True)

    time_created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
