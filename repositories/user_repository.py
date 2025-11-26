from sqlalchemy.orm import Session
from models import UserDB

# ------------------------------
# Repository = Data Access Layer
# This file talks DIRECTLY to the database.
# It SHOULD NOT contain business logic,
# only simple CRUD operations.
# ------------------------------

def get_by_username(db: Session, username: str) -> UserDB | None:
    """
    Fetch a single user by username.
    Returns None if the user does not exist.
    """
    return db.query(UserDB).filter(UserDB.username == username).first()


def create_user(db: Session, username: str, password: str, is_admin: bool) -> UserDB:
    """
    Create a new user in the database.
    NOTE: No hashing here — because this is done in the SERVICE layer (if required).
    This function ONLY inserts to DB.
    """
    user = UserDB(username=username, password=password, is_admin=is_admin)
    db.add(user)
    db.commit()          # save changes
    db.refresh(user)     # reload object from DB with ID
    return user


def set_admin(db: Session, username: str, is_admin: bool) -> UserDB:
    """
    Update the user's admin flag.
    If user does not exist → return None (service layer will handle the error).
    """
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        return None

    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session) -> list[UserDB]:
    """
    Return all users in the database.
    Admin filtering is handled in service layer (permissions).
    """
    return db.query(UserDB).all()
