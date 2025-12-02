from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_db, get_current_user, ensure_admin
from schemas.user_schema import RegisterRequest, UserOut

# שינוי עיקרי: הפסקנו לייבא מה-Service, עברנו לייבא את ה-Controller
from controllers.user_controller import UserController

# All endpoints here are under the /users prefix and tagged as "Users" in Swagger.
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserOut, status_code=201)
def register(
    # Request body schema validation (Pydantic model)
    data: RegisterRequest,
    # DB session per-request
    db: Session = Depends(get_db),
):
    # שינוי: יצירת הקונטרולר והעברת הטיפול אליו
    # (הבדיקה אם ה-DB קיים מתבצעת בתוך ה-__init__ של הקונטרולר)
    controller = UserController(db)
    return controller.register(data)

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
    
    # שינוי: שימוש בקונטרולר לביצוע הפעולה (True = מנהל)
    controller = UserController(db)
    return controller.update_admin_status(username, make_admin=True)

@router.put("/{username}/demote", response_model=UserOut)
def demote_user(
    username: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only admins can demote others.
    ensure_admin(current_user)
    
    # שינוי: שימוש בקונטרולר לביצוע הפעולה (False = משתמש רגיל)
    controller = UserController(db)
    return controller.update_admin_status(username, make_admin=False)

@router.get("", response_model=list[UserOut])
def list_all_users(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only admins can list all users (sensitive operation).
    ensure_admin(current_user)
    
    # שינוי: שימוש בקונטרולר לשליפת הרשימה
    controller = UserController(db)
    return controller.list_all()