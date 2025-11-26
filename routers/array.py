from fastapi import APIRouter, Depends
from core.security import get_current_user, ensure_admin
from schemas.array_schema import ArrayItem
from services import array_service as svc

# ------------------------------
# Router = HTTP Layer
# This file ONLY defines:
# - URLs
# - HTTP methods
# - dependencies (auth)
# - mapping to service functions
# No business logic here!
# ------------------------------

router = APIRouter(prefix="/array", tags=["Array"])


@router.get("")
def get_array(current_user = Depends(get_current_user)):
    """
    GET /array
    Returns the entire array.
    Only requires authenticated user (no admin).
    """
    return {"array": svc.get_all()}


@router.get("/{index}")
def get_value(index: int, current_user = Depends(get_current_user)):
    """
    GET /array/{index}
    Returns a value by index.
    Validation (range checks) happens in service layer.
    """
    return svc.get_by_index(index)


@router.post("", status_code=201)
def add_value(item: ArrayItem, current_user = Depends(get_current_user)):
    """
    POST /array
    Add a new value to the array.
    Requires ADMIN.
    """
    ensure_admin(current_user)
    return {"array": svc.add(item.value)}


@router.put("/{index}")
def update_value(index: int, item: ArrayItem, current_user = Depends(get_current_user)):
    """
    PUT /array/{index}
    Replace array[index] = new_value.
    Requires ADMIN.
    """
    ensure_admin(current_user)
    return svc.update(index, item.value)


@router.delete("")
def delete_last(current_user = Depends(get_current_user)):
    """
    DELETE /array
    Remove the last element from the array.
    Requires ADMIN.
    """
    ensure_admin(current_user)
    return svc.delete_last()


@router.delete("/{index}")
def reset_by_index(index: int, current_user = Depends(get_current_user)):
    """
    DELETE /array/{index}
    Reset array[index] = 0 according to assignment.
    Requires ADMIN.
    """
    ensure_admin(current_user)
    return svc.reset_index(index)
