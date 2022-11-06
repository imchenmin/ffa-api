from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Union

from fast_firs_aid_server import models, crud, schemas, mypassword
from fast_firs_aid_server.database import SessionLocal, engine


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





def authenticate_user_by_id(db, user_id: str, password: str):
    user = crud.get_user(db, user_id=user_id)
    if not user:
        return False
    if not password.verify_password(password, user.hashed_password):
        return False
    return user


# TODO
def authenticate_user_by_phone_number(db, phone_number: str, password: str):
    user = crud.get_user_by_phone_number(db, phone_number=phone_number)
    if not user:
        return False
    if not mypassword.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, mypassword.SECRET_KEY, algorithm=mypassword.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),  db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, mypassword.SECRET_KEY, algorithms=[mypassword.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_phone_number(db=db, phone_number=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db)):
    user = authenticate_user_by_phone_number(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=mypassword.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone_number}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: schemas.User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.phone_number}]


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    print(items)
    return items

# TODO 添加只有本人能看到
@app.get("/users/{user_id}/aid_items/", response_model=list[schemas.AidItem])
def read_items(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_aid_items_by_initiator_id(db, initiator_id=user_id, skip=skip, limit=limit)
    return items

@app.post("/users/{user_id}/aid_items/", response_model=schemas.AidItem)
def create_aid_item_for_user(
    user_id: int, aid_item: schemas.AidItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_aid_item(db=db, aid_item=aid_item, user_id=user_id)