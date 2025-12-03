from fastapi import APIRouter, Depends

from core.security import get_current_user, ensure_admin
from schemas.user_schema import RegisterRequest, UserOut

# מייבאים גם את המחלקה וגם את פונקציית ה-Dependency
from controllers.user_controller import UserController, get_user_controller

# All endpoints here are under the /users prefix and tagged as "Users" in Swagger.
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserOut, status_code=201)
def register(
    data: RegisterRequest,
    controller: UserController = Depends(get_user_controller)
):
    return controller.register(data)

@router.put("/{username}/promote", response_model=UserOut)
def promote_user(
    username: str,
    current_user = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    ensure_admin(current_user)
    return controller.update_admin_status(username, make_admin=True)

@router.put("/{username}/demote", response_model=UserOut)
def demote_user(
    username: str,
    current_user = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    ensure_admin(current_user)
    return controller.update_admin_status(username, make_admin=False)

@router.get("", response_model=list[UserOut])
def list_all_users(
    current_user = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    ensure_admin(current_user)
    return controller.list_all()