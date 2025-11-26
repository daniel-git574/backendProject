# backend-project/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base

# ============================================================
# ORM MODELS (DB SCHEMA)
# Each class here represents a table in the PostgreSQL database.
# Each class attribute represents a column.
# ============================================================

class UserDB(Base):
    __tablename__ = "users"  # Table name in PostgreSQL

    # Primary key column
    id = Column(Integer, primary_key=True, index=True)

    # Username - must be unique
    username = Column(String(50), unique=True, nullable=False, index=True)

    # Password - stored as plain text only because of assignment requirements
    password = Column(String(255), nullable=False)

    # Whether the user is an admin (True/False)
    is_admin = Column(Boolean, nullable=False, default=False)

    # Timestamp - automatically set by PostgreSQL using NOW()
    created_at = Column(DateTime, server_default=func.now())
