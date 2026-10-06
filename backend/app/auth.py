import os
import time
from typing import Optional

import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from passlib.context import CryptContext

from .database import SessionLocal, User

SECRET_KEY = os.getenv("SECRET_KEY", "educollab-dev-secret-key-32-bytes-minimum!")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalizar_senha(password: str) -> str:
    return password[:72]


def hash_password(password: str) -> str:
    return pwd_context.hash(_normalizar_senha(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_normalizar_senha(plain_password), hashed_password)


def create_access_token(email: str, tipo: str) -> str:
    payload = {
        "sub": email,
        "tipo": tipo,
        "exp": int(time.time()) + 3600 * 8,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.") from exc


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = None):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticação ausente.")
    token = credentials.credentials
    payload = decode_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem usuário válido.")
    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
    return user
