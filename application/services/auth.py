from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from config.config import Config
from fastapi import Request

from fastapi import Request, HTTPException
from jose import jwt, JWTError 

config = Config.load()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config.key
ALGORITHM = "HS256"

def hash_password(password: str):
    print(password)
    hashed = pwd_context.hash(password)
    return hashed

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Please login"
        )
    token = auth_header.split(" ")[1] # why?
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    user_id = payload.get("user_id")
    username = payload.get("username")

    return {"user_id": user_id, "username": username}