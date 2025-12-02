import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


from routers import auth, users, array
# from core.config import settings  # ← בטל/הפעל לפי שימוש
from database import Base, engine
from core.security import get_current_user  # לאימות ב-/health

app = FastAPI(
    title="FastAPI Exercise - Layered Architecture",
    version="1.0.0"
)


#  ERROR HANDLERS (Global Exception Handling)
# ---------------------------------------------------------
# טיפול בשגיאות HTTP רגילות
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "success": False}
    )

# 2. טיפול בשגיאות ולידציה (כשמישהו שולח JSON לא תקין)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "Validation Error"}
    )

#  תופס שגיאות לא צפויות (קריסות שרת - 500)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # לוג למתכנת כדי שתוכלו לתקן את הבאג
    print(f" CRITICAL UNEXPECTED ERROR: {exc}")
    
    # תשובה ללקוח
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "An unexpected error occurred. Please contact support.",
            "error_type": "Internal Server Error"
        },
    )

# Include Routers
# -----------------
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