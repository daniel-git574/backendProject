from fastapi import APIRouter, Depends
from core.security import get_current_user, ensure_admin
from schemas.array_schema import ArrayItem
from controllers.array_controller import ArrayController, get_array_controller

router = APIRouter(prefix="/array", tags=["Array"])

@router.get("")
def get_array(
    current_user = Depends(get_current_user),
    controller: ArrayController = Depends(get_array_controller)
):
    """
    GET /array
    Returns the entire array.
    """
    return controller.get_all()


@router.get("/{index}")
def get_value(
    index: int, 
    current_user = Depends(get_current_user),
    controller: ArrayController = Depends(get_array_controller)
):
    """
    GET /array/{index}
    Returns a value by index.
    """
    return controller.get_by_index(index)


@router.post("", status_code=201)
def add_value(
    item: ArrayItem, 
    current_user = Depends(get_current_user),
    controller: ArrayController = Depends(get_array_controller)
):
    """
    POST /array
    Add a new value. Requires ADMIN.
    """
    ensure_admin(current_user)
    return controller.add_value(item.value)


@router.put("/{index}")
def update_value(
    index: int, 
    item: ArrayItem, 
    current_user = Depends(get_current_user),
    controller: ArrayController = Depends(get_array_controller)
):
    """
    PUT /array/{index}
    Replace value. Requires ADMIN.
    """
    ensure_admin(current_user)
    return controller.update_value(index, item.value)


@router.delete("")
def delete_last(
    current_user = Depends(get_current_user),
    controller: ArrayController = Depends(get_array_controller)
):
    """
    DELETE /array
    Remove last element. Requires ADMIN.
    """
    ensure_admin(current_user)
    return controller.delete_last()


@router.delete("/{index}")
def reset_by_index(
    index: int, 
    current_user = Depends(get_current_user),
    controller: ArrayController = Depends(get_array_controller)
):
    """
    DELETE /array/{index}
    Reset to 0. Requires ADMIN.
    """
    ensure_admin(current_user)
    return controller.reset_index(index)