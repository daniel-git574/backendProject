from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_db, get_current_user, ensure_admin
from schemas.user_schema import RegisterRequest, UserOut
from services.user_service import register_user, promote, demote, list_users

# All endpoints here are under the /users prefix and tagged as "Users" in Swagger.
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserOut, status_code=201)
def register(
    # Request body schema validation (Pydantic model)
    data: RegisterRequest,
    # DB session per-request
    db: Session = Depends(get_db),
):
    # Hand off to service layer: creates user, handles admin-secret logic, returns sanitized UserOut.
    return register_user(db, data)

@router.put("/{username}/promote", response_model=UserOut)
def promote_user(
    # Path param captured from /users/{username}/promote
    username: str,
    # Require a valid JWT and get the current user
    current_user = Depends(get_current_user),
    # DB session
    db: Session = Depends(get_db),
):
    # Ensure the *caller* is admin (not the target user).
    ensure_admin(current_user)
    # Service does the actual promotion (sets is_admin=True), returns updated user.
    return promote(db, username)

@router.put("/{username}/demote", response_model=UserOut)
def demote_user(
    username: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only admins can demote others.
    ensure_admin(current_user)
    return demote(db, username)

@router.get("", response_model=list[UserOut])
def list_all_users(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only admins can list all users (sensitive operation).
    ensure_admin(current_user)
    # Returns a list of UserOut (no passwords, only safe fields).
    return list_users(db)




