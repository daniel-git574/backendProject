"""
Security helpers and dependencies used across the app.

What's inside:
- DB session dependency (get_db)
- Small user helper (get_user_by_username)
- JWT creation (create_access_token)
- "Who am I?" dependency that decodes JWT and returns current user (get_current_user)
- "Admin gate" that enforces admin-only access (ensure_admin)
- Password Hashing utilities (bcrypt)
"""

from datetime import datetime, timedelta
from typing import Generator

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext  #encryption library
from sqlalchemy.orm import Session

from database import SessionLocal
from models import UserDB
from schemas.user_schema import UserOut
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme

# === Password Hashing Config ===
#(bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# === DB session per request ===
def get_db() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy Session for the duration of a single request.
    FastAPI will:
      - call this before the endpoint (open session)
      - run the endpoint
      - finally block closes the session after the endpoint returns/raises
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === helpers ===
def get_user_by_username(db: Session, username: str) -> UserDB | None:
    """
    Simple repository-style helper.
    Returns the UserDB row by unique username, or None if not found.
    """
    return db.query(UserDB).filter(UserDB.username == username).first()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a signed JWT.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# === auth dependencies ===
def get_current_user(
    token: str = Depends(oauth2_scheme),  # extracts Bearer token from Authorization header
    db: Session = Depends(get_db),
) -> UserOut:
    """
    FastAPI dependency that decodes token and returns current user.
    """
    cred_exc = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode & verify JWT (raises JWTError on invalid/expired tokens)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        is_admin: bool | None = payload.get("is_admin")
        if username is None or is_admin is None:
            # Missing expected claims -> invalid token
            raise cred_exc
    except JWTError:
        # Any JWT decoding/verification error -> unauthorized
        raise cred_exc

    # Ensure the user still exists in the DB (token may outlive user deletion)
    db_user = get_user_by_username(db, username)
    if db_user is None:
        raise cred_exc

    # Return a sanitized data model (not the ORM row)
    return UserOut(username=db_user.username, is_admin=db_user.is_admin)


def ensure_admin(current_user: UserOut):
    """
    Guard used inside endpoints to enforce admin-only operations.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")