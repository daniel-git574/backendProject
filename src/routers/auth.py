from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from core.security import get_current_user
from schemas.token_schema import TokenResponse

# מייבאים גם את המחלקה וגם את פונקציית ה-Dependency
from controllers.auth_controller import AuthController, get_auth_controller

# No prefix → /login stays exactly at /login
router = APIRouter(tags=["Auth"])

# -----------------------
# LOGIN (OAuth2 password)
# -----------------------
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller),
):
    return controller.login(form_data.username, form_data.password)

# -----------------------
# Who am I (protected)
# -----------------------
@router.get("/me")
def me(current_user = Depends(get_current_user)):
    return {"user": current_user.username}

# -----------------------
# Echo (protected)
# -----------------------
@router.get("/echo")
def echo_message(
    msg: str,
    current_user = Depends(get_current_user),
):
    return {"echo": f"The message is {msg}", "user": current_user.username}