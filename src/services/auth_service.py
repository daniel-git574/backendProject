from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from core.security import create_access_token, verify_password
# שינוי: ייבוא המחלקה
from repositories.user_repository import UserRepository
from schemas.token_schema import TokenResponse

def login(db: Session, username: str, password: str) -> TokenResponse:
    repo = UserRepository(db) # אתחול

    # Fetch user record from DB by username
    # שימוש ב-repo
    db_user = repo.get_by_username(username)

    # Login check
    if db_user is None or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Payload
    token_data = {
        "sub": db_user.username,
        "is_admin": db_user.is_admin
    }

    # Create JWT
    token = create_access_token(
        token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(access_token=token, token_type="bearer")