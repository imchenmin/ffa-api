from datetime import timedelta, datetime

from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, desc

from fast_firs_aid_server import models, schemas, mypassword


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email,
                          hashed_password=mypassword.get_password_hash(user.hashed_password),
                          phone_number=user.phone_number,
                          real_name=user.real_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#TODO demo内容，待删
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

#TODO demo内容，待删
def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_user_aid_item(db: Session, aid_item: schemas.AidItemCreate, user_id: int):
    db_item = models.AidItem(**aid_item.dict(), initiator_id=user_id)
    print(aid_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_aid_item_response_item(db: Session, response_item: schemas.ResponseItem, aid_item_id: int):
    db_item = models.ResponseItem(**response_item.dict(), initiator_id=aid_item_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_aid_items_by_initiator_id(db: Session, initiator_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.AidItem).filter(models.AidItem.initiator_id == initiator_id).all()


def create_location_item(db: Session, user: schemas.User, lon: float, lat:float):
    db_location = models.LocationItem(user_id=user.id,lon=lon, lat=lat)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

"""
查询地理位置，获取一定时间内的用户的位置信息。每一个用户只显示一个
"""
def get_unique_users_location(db: Session, time_delta=5):
    # 也不知道怎么写的
    rownb = func.row_number().over(order_by=models.LocationItem.time_created.desc()
                                   , partition_by=models.LocationItem.user_id)
    rownb = rownb.label('rownb')

    subq = db.query(models.LocationItem, rownb)  # add interesting filters here

    subq = subq.subquery(name="subq", with_labels=True)
    return db.query(aliased(models.LocationItem, alias=subq)).filter(subq.c.rownb == 1)\
        .filter(models.LocationItem.time_created >= datetime.utcnow() - timedelta(minutes=time_delta))\
        .all()
    # return db.query(models.LocationItem)\
    #     .filter(models.LocationItem.time_created >= datetime.utcnow() - timedelta(minutes=time_delta))\
    #     .group_by(models.LocationItem.user_id)\
    #     .order_by(models.LocationItem.time_created).all()

def get_all_user_location(db: Session):
    return db.query(models.LocationItem).order_by(models.LocationItem.time_created).limit(20).all()