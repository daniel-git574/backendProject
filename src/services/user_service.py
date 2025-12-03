from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.security import get_password_hash
from core.config import ADMIN_SECRET
from repositories.user_repository import UserRepository 
from schemas.user_schema import RegisterRequest, UserOut


def register_user(db: Session, data: RegisterRequest) -> UserOut:
    # אתחול ה-Repository עם החיבור לדאטה-בייס
    repo = UserRepository(db)

    # Check if username already exists
    # שימוש במחלקה: repo.get_by_username
    existing = repo.get_by_username(data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Determine if new user should be admin
    is_admin = False

    # If admin_secret is provided → validate it
    if data.admin_secret not in (None, ""):
        if data.admin_secret != ADMIN_SECRET:
            raise HTTPException(status_code=403, detail="Invalid admin secret")
        is_admin = True

    # Hash the password
    hashed_password = get_password_hash(data.password)

    # Create user in the database
    new_user = repo.create_user(data.username, hashed_password, is_admin)

    return UserOut(username=new_user.username, is_admin=new_user.is_admin)


def update_admin_status(db: Session, username: str, make_admin: bool) -> UserOut:
    """
    Unified function to promote or demote a user.
    """
    repo = UserRepository(db) # אתחול

    # 1. Find user
    user = repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Check logic
    if user.is_admin == make_admin:
        status_str = "an admin" if make_admin else "a regular user"
        raise HTTPException(status_code=400, detail=f"User is already {status_str}")

    # 3. Update status
    user = repo.set_admin(username, make_admin)
    return UserOut(username=user.username, is_admin=user.is_admin)


def list_users(db: Session) -> list[UserOut]:
    repo = UserRepository(db)
    
    # Fetch all users
    return [
        UserOut(username=u.username, is_admin=u.is_admin)
        for u in repo.list_users()
    ]