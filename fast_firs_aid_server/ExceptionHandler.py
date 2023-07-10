from fastapi import HTTPException, status
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

websocket_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Could not handle multiply connection for the same user",
    headers={"WWW-Authenticate": "Bearer"},
)
# TODO 将所有的异常处理写到这里