from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from core.security import get_db, get_current_user
from schemas.token_schema import TokenResponse
# שינוי 1: מחקנו את הייבוא הישן מה-Service
# והוספנו ייבוא של הקונטרולר החדש
from controllers.auth_controller import AuthController

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
    # שינוי 2: במקום לקרוא לפונקציית שירות, אנחנו יוצרים את הקונטרולר
    # ומעבירים לו את ה-DB (הבדיקה אם ה-DB תקין קורית בתוך הקונטרולר)
    controller = AuthController(db)
    
    # הקונטרולר מטפל בלוגיקה ומחזיר את הטוקן
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