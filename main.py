from fastapi import FastAPI, Depends
from routers import auth, users, array
# from core.config import settings  # ← בטל/הפעל לפי שימוש
from database import Base, engine
from core.security import get_current_user  # לאימות ב-/health

app = FastAPI(
    title="FastAPI Exercise - Layered Architecture",
    version="1.0.0"
)

# ------------------
# Include Routers
# ------------------
# auth.router  → login + token issuing
# users.router → register/promote/demote/list (admin ops)
# array.router → in-memory array CRUD (admin for write ops)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(array.router)

# ------------------
# Public root: liveness/info
# ------------------
@app.get("/")
def root():
    return {"msg": "API is running"}

# ------------------
# Protected health: requires JWT
# ------------------
@app.get("/health")
def health(current_user = Depends(get_current_user)):
    return {"status": "ok", "user": current_user.username}

# ------------------
# Dev-only: create tables on startup (no schema migrations)
# ------------------
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)





