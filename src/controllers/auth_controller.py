from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services import auth_service
from schemas.token_schema import TokenResponse

class AuthController:
    def __init__(self, db: Session):
        
        
        if not db:
            raise HTTPException(status_code=500, detail="Database session is missing")
        self.db = db

    def login(self, username: str, password: str) -> TokenResponse:
        """
        הקונטרולר מקבל את השם והסיסמה ומעביר לטיפול הסרוויס
        """
        return auth_service.login(self.db, username, password)

def get_auth_controller(db: Session = Depends(get_db)) -> AuthController:
    return AuthController(db)