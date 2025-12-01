from sqlalchemy.orm import Session
from fastapi import HTTPException

# אנחנו מייבאים את הלוגיקה מה-Service ואת הסכמות
from services import user_service
from schemas.user_schema import RegisterRequest, UserOut

class UserController:
    def __init__(self, db: Session):
        # הערה 6: הקונטרולר מקבל את ה-Session ומוודא שהוא קיים
        if not db:
            raise HTTPException(status_code=500, detail="Database session is missing")
        self.db = db

    def register(self, data: RegisterRequest) -> UserOut:
        # הקונטרולר מפעיל את הסרוויס
        return user_service.register_user(self.db, data)

    def update_admin_status(self, username: str, make_admin: bool) -> UserOut:
        # הקונטרולר מפעיל את פונקציית העדכון (המאוחדת שיצרנו)
        return user_service.update_admin_status(self.db, username, make_admin)

    def list_all(self) -> list[UserOut]:
        return user_service.list_users(self.db)