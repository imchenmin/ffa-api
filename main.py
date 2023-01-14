import json

from fastapi import Depends, FastAPI, HTTPException, status, Request, WebSocket, WebSocketDisconnect, Query, Cookie
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Union, Optional
from fast_firs_aid_server.ExceptionHandler import credentials_exception, websocket_exception
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from fast_firs_aid_server import models, crud, schemas, mypassword
from fast_firs_aid_server.database import SessionLocal, engine

from solver.solver import solver

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# sio = socketio.AsyncServer(async_mode='asgi')
# # app绑定socketio
# app.mount('/', socketio.ASGIApp(socketio_server=sio))  # 使用默认的socket path

@app.middleware("http")
async def TestCustomMiddleware(request: Request, call_next):
    the_headers = request.headers


    response = await call_next(request)
    return response


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


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user_by_phone_number(db, form_data.username, form_data.password)
    if not user:
        raise credentials_exception
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


class ConnectionManager:
    """
    一个user同时只能有一个websocket连接
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.active_connections_user_ids: list[int] = []

    async def connect(self, websocket: WebSocket, user: schemas.User):
        await websocket.accept()
        if user.id in self.active_connections_user_ids:
            raise WebSocketDisconnect(reason="同一个用户最多只能拥有一个websocket连接")
            return
        self.active_connections.append(websocket)
        self.active_connections_user_ids.append(user.id)

    def close(self, websocket: WebSocket):
        websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        idx: int = self.active_connections.index(websocket)
        self.active_connections.remove(websocket)
        self.active_connections_user_ids.pop(idx)

    def disconnect(self, websocket: WebSocket):
        idx: int = self.active_connections.index(websocket)
        self.active_connections.remove(websocket)
        self.active_connections_user_ids.pop(idx)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_message_json(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    def get_websocket_by_user_id(self, user_id: int):
        if user_id not in self.active_connections_user_ids:
            raise websocket_exception
        user_id_idx = self.active_connections_user_ids.index(user_id)
        return self.active_connections[user_id_idx]

    def get_websocket_by_user(self, user: schemas.User):
        pass


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
           <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">链接</button>
            <hr>
            <label>消息: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>发送</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var token = document.getElementById("token")
                ws = new WebSocket("ws://10.27.132.158:8012/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
</script>
    </body>
</html>
"""


@app.get("/wstest/")
async def get():
    return HTMLResponse(html)


manager = ConnectionManager()


async def get_cookie_or_token(
        websocket: WebSocket,
        session: Optional[str] = Cookie(None),
        token: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):
    try:
        print(token)
        payload = jwt.decode(token, mypassword.SECRET_KEY, algorithms=[mypassword.ALGORITHM])
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_phone_number(db=db, phone_number=token_data.username)
    if user is None or user.disabled == True:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return user


@app.get("/location_test/", response_model=list[schemas.LocationItem])
async def test_getlocation(db: Session = Depends(get_db)):
    return crud.get_unique_users_location(db, time_delta=600)


def handle_location(current_active_user: schemas.User, db: Session, loc_data: dict):
    crud.create_location_item(db, current_active_user, loc_data.get("lon", 0), loc_data.get("lat", 0))


# , response_model=schemas.AidItem
@app.post("/first_aid/")
async def create_firstaid_item(aid_item: schemas.AidItemCreate,
                               current_user: schemas.User = Depends(get_current_active_user),
                               db: Session = Depends(get_db)):
    """
    # target_users: list[schemas.User] = []
    # for user in target_users:
    #     # 路线位置获得
    #     #装配发送体
    #
    #     # 创建response返回体
    #     response = dict()
    #     response['msg_type'] = "first_aid_request"
    #     response['help_seeker_location'] = {"lon": 0, "lat": 0}
    #     response['routers'] = {"hereby"}
    #     response['id'] = db_aid_item.id
    #     response['initiator_id'] = db_aid_item.initiator_id
    #     websocket = manager.get_websocket_by_user_id(user.id)
    #     websocket.send_text(str(response))
    # 在handle_confirm中建立双向的实时救援路线和地点。
    :param aid_item:
    :param current_user:
    :param db:
    :return:
    """
    print("receive first aid request from " + current_user.phone_number)
    location_items: list[schemas.LocationItem] = crud.get_unique_users_location(db, time_delta=600)
    path_user = dict()
    response = []
    for item in location_items:
        path_user[item.user_id] = {'lon': item.lon, 'lat': item.lat}
        response.append({'lon': item.lon, 'lat': item.lat, 'id': item.user_id})
    current_user_location = path_user[current_user.id]
    end_point = [current_user_location['lon'],current_user_location['lat']]

    path_dict: dict = solver(end_point, response) # 算法入口
    for user_id in path_dict.keys():
        print("active_connections_user_ids", manager.active_connections_user_ids)
        if user_id in manager.active_connections_user_ids:
            print("userid", user_id)
            idx: int = manager.active_connections_user_ids.index(user_id)
            if current_user.id == user_id:
                # 不给自己发请求
                continue
            websocket = manager.active_connections[idx]
            response_dict = dict()
            response_dict['route'] = path_dict[user_id]
            response_dict['type'] = "first_aid_request"
            response_dict['request_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_user = path_user[user_id]
            response_dict['start_point'] = [response_user['lon'], response_user['lat']]
            response_dict['end_point'] = end_point
            print(response_dict)
            await manager.send_personal_message_json(jsonable_encoder(response_dict), websocket)
            # await manager.broadcast(f"Clinet {user_id} received first_aid_request")

            print(user_id)
    print(path_dict)
    return JSONResponse(json.dumps(path_dict))
    # return crud.create_user_aid_item(db, aid_item, current_user.id)



@app.get("/solver/")
async def solver_test(db: Session = Depends(get_db)):
    location_items: list[schemas.LocationItem] = crud.get_unique_users_location(db, time_delta=60000)
    # location_items = [{"id": item.user_id, "lon": item.lon, 'lat': item.lat} for item in location_items]
    path_user = dict()
    response = []
    for item in location_items:
        path_user[item.user_id] = {'lon': item.lon, 'lat': item.lat}
        response.append({'lon': item.lon, 'lat': item.lat, 'id': item.user_id})
    end_point = [114.000591, 22.598331]
    response = [
        {
            "id": 1,
            "lon": 114.002946,
            "lat": 22.601137  # 松禾体育场
        },
        {
            "id": 2,
            "lon": 114.002451,
            "lat": 22.599728  # 教师公寓4号楼
        },
        {
            "id": 42,
            "lon": 113.995814,
            "lat": 22.594767  # 台州楼
        },
        {
            "id": 25,
            "lon": 113.998378,
            "lat": 22.595084  # 琳恩图书馆
        },
        {
            "id": 37,
            "lon": 114.00076,
            "lat": 22.595252  # 商学院
        },
        {
            "id": 72,
            "lon": 113.995653,
            "lat": 22.59961  # 工学院大楼
        }
    ]
    path_dict: dict = solver(end_point, response)
    print(path_dict)
    for user_id in path_dict.keys():
        print("active_connections_user_ids", manager.active_connections_user_ids)
        if user_id in manager.active_connections_user_ids:
            print("userid", user_id)
            idx: int = manager.active_connections_user_ids.index(user_id)
            websocket = manager.active_connections[idx]
            response_dict = dict()
            response_dict['route'] = path_dict[user_id]
            response_dict['type'] = "first_aid_request"
            response_dict['request_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_user = path_user[user_id]
            response_dict['start_point'] = [response_user['lon'], response_user['lat']]
            response_dict['end_point'] = end_point
            print(response_dict['route'])
            print("non", json.dumps(response_dict))
            await manager.send_personal_message_json(jsonable_encoder(response_dict), websocket)
            # await manager.broadcast(f"Clinet {user_id} received first_aid_request")

            print(user_id)
    print(path_dict)
    return JSONResponse(json.dumps(path_dict))


def handle_confirm(current_active_user: schemas.User, db: Session, loc_data: dict):
    pass


# TODO 加密
@app.websocket("/ws")
# 接收长连接，主要是位置信息。还有维持长连接。方便用其他函数发送长连接。
async def websocket_endpoint(websocket: WebSocket, current_active_user: schemas.User = Depends(get_cookie_or_token),
                             db: Session = Depends(get_db)):
    await manager.connect(websocket, current_active_user)
    try:
        while True:
            data = await websocket.receive_text()
            json_data: dict = json.loads(data)
            msg_type: str = json_data.get('msg_type', 'non')
            # if not json_data.get("errorCode",-1) == 0:
            #     continue
            if msg_type == "location":
                handle_location(current_active_user, db, json_data)
            elif msg_type == "accept_request":
                # 确认帮助请求
                pass
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client {current_active_user.phone_number}  says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the chat")

# app.include_router(api_router, dependencies=[Depends(log_request_info)])
