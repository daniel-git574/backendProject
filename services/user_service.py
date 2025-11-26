from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import ADMIN_SECRET
from repositories.user_repository import (
    get_by_username,
    create_user,
    set_admin,
    list_users as repo_list
)
from schemas.user_schema import RegisterRequest, UserOut


def register_user(db: Session, data: RegisterRequest) -> UserOut:
    # Check if username already exists
    existing = get_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Determine if new user should be admin
    is_admin = False

    # If admin_secret is provided → validate it
    if data.admin_secret not in (None, ""):
        if data.admin_secret != ADMIN_SECRET:
            # User attempted to register as admin with wrong secret
            raise HTTPException(status_code=403, detail="Invalid admin secret")
        is_admin = True

    # Create user in the database
    new_user = create_user(db, data.username, data.password, is_admin)

    # Return clean user data (without password)
    return UserOut(username=new_user.username, is_admin=new_user.is_admin)


def promote(db: Session, username: str) -> UserOut:
    # Find user to promote
    user = get_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cannot promote someone who is already admin
    if user.is_admin:
        raise HTTPException(status_code=400, detail="User is already an admin")

    # Promote user to admin
    user = set_admin(db, username, True)
    return UserOut(username=user.username, is_admin=user.is_admin)


def demote(db: Session, username: str) -> UserOut:
    # Find user to demote
    user = get_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cannot demote a regular user
    if not user.is_admin:
        raise HTTPException(status_code=400, detail="User is already regular")

    # Set admin = False
    user = set_admin(db, username, False)
    return UserOut(username=user.username, is_admin=user.is_admin)


def list_users(db: Session) -> list[UserOut]:
    # Fetch all users and convert DB objects → Pydantic objects
    return [
        UserOut(username=u.username, is_admin=u.is_admin)
        for u in repo_list(db)
    ]
