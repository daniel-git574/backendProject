# backend-project/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================
# DATABASE CONFIGURATION
# This file is responsible for:
# - Creating the connection to the PostgreSQL database
# - Creating the SQLAlchemy Engine (the “gateway” to the DB)
# - Creating the Session factory (used per request)
# - Creating the Base class (parent for all ORM models)
# ============================================================

# ------------------------------------------------------------
# 1. Database connection string
# Format:
# postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
# ------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/node_exercise"

# ------------------------------------------------------------
# 2. Engine
# The engine manages all low-level communication with PostgreSQL.
# echo=True: shows executed SQL in the terminal (useful for debugging).
# ------------------------------------------------------------
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# ------------------------------------------------------------
# 3. SessionLocal
# This is a factory that creates DB sessions.
# Each request in FastAPI gets its own session via Depends(get_db).
# ------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------------------------------------
# 4. Base
# All ORM models (tables) inherit from this Base class.
# SQLAlchemy uses Base.metadata to create tables.
# ------------------------------------------------------------
Base = declarative_base()

# ------------------------------------------------------------
# OPTIONAL:
# Running this file directly (python database.py)
# will create all tables defined in models.py.
# Very useful in development environments.
# ------------------------------------------------------------
if __name__ == "__main__":
    from models import UserDB  # Import models so SQLAlchemy registers them

    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
