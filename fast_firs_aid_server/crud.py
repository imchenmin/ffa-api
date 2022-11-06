from sqlalchemy.orm import Session

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
