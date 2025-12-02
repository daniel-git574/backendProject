from sqlalchemy.orm import Session
from fastapi import HTTPException

from services import array_service

class ArrayController:
    def __init__(self, db: Session):
        # דרישה 6: מוודאים שה-Session קיים (שומר על אחידות עם שאר הקונטרולרים)
        if not db:
            raise HTTPException(status_code=500, detail="Database session is missing")
        self.db = db

    def get_all(self):
        # הקונטרולר עוטף את התשובה במבנה הרצוי
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