"""SatQuery AI - Auth Routes (JWT-based)"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import get_settings

settings = get_settings()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

try:
    import bcrypt

    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
        except Exception:
            return False
except ImportError:
    import hashlib

    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password

# In-memory user store for development (replace with DB in production)
_DEMO_USERS = {
    "analyst@satquery.ai": {
        "email": "analyst@satquery.ai",
        "full_name": "Demo Analyst",
        "hashed_password": hash_password("satquery2026"),
        "role": "analyst",
    }
}


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user_email: str
    role: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = _DEMO_USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token({"sub": user["email"], "role": user["role"]})
    return Token(
        access_token=token,
        token_type="bearer",
        user_email=user["email"],
        role=user["role"],
    )


@router.post("/register")
async def register(user_data: UserCreate):
    if user_data.email in _DEMO_USERS:
        raise HTTPException(status_code=400, detail="Email already registered.")
    _DEMO_USERS[user_data.email] = {
        "email": user_data.email,
        "full_name": user_data.full_name or "",
        "hashed_password": hash_password(user_data.password),
        "role": "analyst",
    }
    return JSONResponse(content={"message": "Registration successful."})


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token.")
        user = _DEMO_USERS.get(email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found.")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")
