from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services import array_service

class ArrayController:
    def __init__(self, db: Session):
    
        if not db:
            raise HTTPException(status_code=500, detail="Database session is missing")
        self.db = db

    def get_all(self):
        return {"array": array_service.get_all()}

    def get_by_index(self, index: int):
        return array_service.get_by_index(index)

    def add_value(self, value):
        return {"array": array_service.add(value)}

    def update_value(self, index: int, value):
        return array_service.update(index, value)

    def delete_last(self):
        return array_service.delete_last()

    def reset_index(self, index: int):
        return array_service.reset_index(index)


def get_array_controller(db: Session = Depends(get_db)) -> ArrayController:
    return ArrayController(db)