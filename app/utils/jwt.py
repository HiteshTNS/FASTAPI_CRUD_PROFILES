# app/utils/jwt.py
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import JWTError, jwt
from app.core.config import settings

SECRET_KEY = settings.db.secret_key
ALGORITHM = settings.db.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.db. jwt_expiration_minutes

# Function to create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to decode the JWT token and return the payload
# def decode_access_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except JWTError:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
