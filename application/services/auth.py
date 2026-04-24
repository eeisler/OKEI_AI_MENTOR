from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from config.config import Config

config = Config.load()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config.key
ALGORITHM = "HS256"

def hash_password(password: str):
    print(password)
    hashed = pwd_context.hash(password)
    print(hashed)
    return 

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
