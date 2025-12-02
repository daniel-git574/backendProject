from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# הוספנו את get_db כדי להעביר אותו לקונטרולר
from core.security import get_current_user, ensure_admin, get_db
from schemas.array_schema import ArrayItem
# שינוי: מייבאים את הקונטרולר במקום את הסרוויס
from controllers.array_controller import ArrayController

router = APIRouter(prefix="/array", tags=["Array"])

@router.get("")
def get_array(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db) # הוספה: קבלת ה-DB
):
    """
    GET /array
    Returns the entire array.
    """
    controller = ArrayController(db)
    return controller.get_all()


@router.get("/{index}")
def get_value(
    index: int, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /array/{index}
    Returns a value by index.
    """
    controller = ArrayController(db)
    return controller.get_by_index(index)


@router.post("", status_code=201)
def add_value(
    item: ArrayItem, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /array
    Add a new value. Requires ADMIN.
    """
    ensure_admin(current_user)
    
    controller = ArrayController(db)
    # שים לב: item.value כבר עבר ולידציה להיות int/str/float בתיקון הקודם
    return controller.add_value(item.value)


@router.put("/{index}")
def update_value(
    index: int, 
    item: ArrayItem, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PUT /array/{index}
    Replace value. Requires ADMIN.
    """
    ensure_admin(current_user)
    
    controller = ArrayController(db)
    return controller.update_value(index, item.value)


@router.delete("")
def delete_last(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DELETE /array
    Remove last element. Requires ADMIN.
    """
    ensure_admin(current_user)
    
    controller = ArrayController(db)
    return controller.delete_last()


@router.delete("/{index}")
def reset_by_index(
    index: int, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DELETE /array/{index}
    Reset to 0. Requires ADMIN.
    """
    ensure_admin(current_user)
    
    controller = ArrayController(db)
    return controller.reset_index(index)