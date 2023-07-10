def init_socketio(app):
    # 事件函数
    async def connect(sid, environ):
        query_params = environ['QUERY_STRING'].split('&')
        params = dict()
        for query_param in query_params:
            a, b = query_param.split('=')
            params[a] = parse.unquote(b)
        user_name = params['name']
        user_sid[user_name] = sid
        await sio.emit('reply', f'{user_name}连线成功！', namespace='/chat')

    async def message(sid, data):
        await sio.emit('reply', f"{user_sid.inv[sid]}: {data}", namespace='/chat')

    async def disconnect(sid):
        user_name = user_sid.inv[sid]
        del user_sid[user_name]
        await sio.emit('reply', f'{user_name}退出连线！', namespace='/chat')

    # 静态文件
    app.mount("/static", StaticFiles(directory=f"{pwd_path}/static"), )

    # 初始化socketio
    sio = socketio.AsyncServer(async_mode='asgi')
    # 绑定事件函数
    sio.on('disconnect', disconnect, namespace='/chat')
    sio.on('chat message', message, namespace='/chat')
    sio.on('connect', connect, namespace='/chat')
    # app绑定socketio
    app.mount('/', socketio.ASGIApp(socketio_server=sio))  # 使用默认的socket path
