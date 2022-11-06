from passlib.context import CryptContext

SECRET_KEY = "f4d102924a51082a00d97afa21eb6b8e2db85384b21d38eb3a4afdd8c2e769d0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)