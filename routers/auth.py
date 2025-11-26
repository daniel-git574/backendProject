from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from core.security import get_db, get_current_user
from schemas.token_schema import TokenResponse
from services.auth_service import login as login_service

# No prefix → /login stays exactly at /login
router = APIRouter(tags=["Auth"])

# -----------------------
# LOGIN (OAuth2 password)
# -----------------------
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Delegate credentials check + JWT issuing to the service layer
    return login_service(db, form_data.username, form_data.password)

# -----------------------
# Who am I (protected)
# -----------------------
@router.get("/me")
def me(current_user = Depends(get_current_user)):
    # Returns the authenticated user's identity
    return {"user": current_user.username}

# -----------------------
# Echo (protected)
# -----------------------
@router.get("/echo")
def echo_message(
    msg: str,
    current_user = Depends(get_current_user),
):
    # Demonstrates query param + auth
    return {"echo": f"The message is {msg}", "user": current_user.username}
