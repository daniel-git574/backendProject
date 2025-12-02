from sqlalchemy.orm import Session
from models import UserDB

class UserRepository:
    def __init__(self, db: Session):
        """
        המחלקה מקבלת את החיבור ל-DB פעם אחת בעת היצירה,
        ושומרת אותו ב-self.db לשימוש בכל הפונקציות.
        """
        self.db = db

    def get_by_username(self, username: str) -> UserDB | None:
        """
        Fetch a single user by username.
        """
        # שימוש ב-self.db במקום לקבל db כפרמטר
        return self.db.query(UserDB).filter(UserDB.username == username).first()

    def create_user(self, username: str, password_hash: str, is_admin: bool) -> UserDB:
        """
        Create a new user in the database.
        """
        # שים לב: אנחנו שומרים password_hash ולא password רגיל (תואם לתיקון האבטחה שעשינו)
        user = UserDB(username=username, password=password_hash, is_admin=is_admin)
        
        self.db.add(user)
        self.db.commit()
        # מחיקת db.refresh(user) - הנתונים כבר אצלנו, חוסכים קריאה ל-DB
        
        return user

    def set_admin(self, username: str, is_admin: bool) -> UserDB | None:
        """
        Update the user's admin flag.
        """
        user = self.get_by_username(username) # שימוש בפונקציה פנימית של המחלקה
        if not user:
            return None

        user.is_admin = is_admin
        self.db.commit()
        # גם כאן הורדנו את ה-refresh המיותר
        
        return user

    def list_users(self) -> list[UserDB]:
        """
        Return all users.
        """
        return self.db.query(UserDB).all()