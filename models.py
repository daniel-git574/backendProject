# backend-project/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base   # שים לב: בלי נקודה לפני database


# ייצוג של טבלת "users" ב-PostgreSQL – המודל UserDB
class UserDB(Base):
    __tablename__ = "users"  # שם הטבלה במסד הנתונים

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())
