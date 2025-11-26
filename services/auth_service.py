from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from core.security import create_access_token
from repositories.user_repository import get_by_username
from schemas.token_schema import TokenResponse

def login(db: Session, username: str, password: str) -> TokenResponse:
    # Fetch user record from DB by username
    db_user = get_by_username(db, username)

    # If user does not exist OR passwords don't match → login fails
    if db_user is None or db_user.password != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Payload that will be inside the JWT token
    token_data = {
        "sub": db_user.username,      # "sub" = subject (username)
        "is_admin": db_user.is_admin  # Admin privileges encoded into token
    }

    # Create a JWT token with expiration time
    token = create_access_token(
        token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Return final token to client
    return TokenResponse(access_token=token, token_type="bearer")
