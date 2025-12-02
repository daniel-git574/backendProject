from sqlalchemy.orm import Session
from fastapi import HTTPException

# מייבאים את הסרוויס של ההתחברות ואת הסכמה של הטוקן
from services import auth_service
from schemas.token_schema import TokenResponse

class AuthController:
    def __init__(self, db: Session):
        """
        בדיוק כמו ב-User, אנחנו מוודאים שה-DB קיים (דרישה 6).
        """
        if not db:
            raise HTTPException(status_code=500, detail="Database session is missing")
        self.db = db

    def login(self, username: str, password: str) -> TokenResponse:
        """
        הקונטרולר מקבל את השם והסיסמה ומעביר לטיפול הסרוויס.
        """
        return auth_service.login(self.db, username, password)