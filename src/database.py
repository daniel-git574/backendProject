# backend-project/database.py
from __future__ import annotations

"""
DATABASE CONFIGURATION

Responsibilities:
- Build the connection string (supports env-first; works in local & Docker)
- Create SQLAlchemy Engine (the “gateway” to PostgreSQL)
- Create the Session factory (used per request)
- Create the Base class (parent for all ORM models)

HOW CONNECTION IS CHOSEN (priority order):
1) If env var DATABASE_URL is set -> use it verbatim.
   - Example: postgresql://postgres:admin@db:5432/node_exercise
2) Otherwise, compose from POSTGRES_* env vars with sensible defaults:
   POSTGRES_USER     (default: postgres)
   POSTGRES_PASSWORD (default: admin)
   POSTGRES_DB       (default: node_exercise)
   POSTGRES_HOST     (default: localhost)   # in Docker Compose: usually 'db'
   POSTGRES_PORT     (default: 5432)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------- Resolve connection string from environment (env-first) ----------
def _build_db_url() -> str:
    # 1) Full URL provided?
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # 2) Compose from parts (works for local & Compose)
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "admin")
    db_name = os.getenv("POSTGRES_DB", "node_exercise")
    host = os.getenv("POSTGRES_HOST", "localhost")  # in Compose: use 'db'
    port = os.getenv("POSTGRES_PORT", "5432")

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

SQLALCHEMY_DATABASE_URL = _build_db_url()

# -------- Engine (echo=True only if you want SQL logs) --------------------
# Tip: you can toggle echo via env (ECHO_SQL=1) if you like.
echo_flag = os.getenv("ECHO_SQL", "0") == "1"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=echo_flag)

# -------- Session factory per-request -------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------- Declarative base for ORM models ---------------------------------
Base = declarative_base()

# -------- Dev helper: create tables when run directly ---------------------
if __name__ == "__main__":
    # Import models so SQLAlchemy registers them
    from models import UserDB
    Base.metadata.create_all(bind=engine)
    print(f"Tables created successfully against: {SQLALCHEMY_DATABASE_URL}")