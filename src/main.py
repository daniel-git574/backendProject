import sys
import os
from contextlib import asynccontextmanager
from sqlalchemy import text

# Add current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from routers import auth, users, array
# from core.config import settings
from database import Base, engine, SessionLocal
from core.security import get_current_user

# ---------------------------------------------------------
# LIFESPAN: Manage Application Startup & Shutdown
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("Server is starting up...")

    # 1. Create Database Tables
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully (or already exist).")
    except Exception as e:
        print(f"Error creating tables: {e}")

    # 2. Database Health Check (Internal Log)
    # This verifies that the API can talk to the DB during startup.
    # Useful for the cloud logs (what the manager sees).
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # Simple query to check connection
        db.close()
        print("DATABASE HEALTH CHECK PASSED: Connection is alive and ready!")
    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: Could not connect to DB! Error: {e}")
        # The server will still start, but logs will show the critical failure.

    yield  # Application runs here...

    # --- SHUTDOWN LOGIC ---
    print("Server is shutting down...")


# Initialize FastAPI with the lifespan manager
app = FastAPI(
    title="FastAPI Exercise - Layered Architecture",
    version="1.0.0",
    lifespan=lifespan
)

# ---------------------------------------------------------
# GLOBAL EXCEPTION HANDLERS
# ---------------------------------------------------------

# 1. Handle standard HTTP exceptions (like 404, 401, 403)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "success": False}
    )

# 2. Handle validation errors (invalid JSON structure or types)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "Validation Error"}
    )

# 3. Handle unexpected server errors (500 - System Crashes)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full error for the developer to debug
    print(f"CRITICAL UNEXPECTED ERROR: {exc}")
    
    # Return a generic friendly message to the client
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "An unexpected error occurred. Please contact support.",
            "error_type": "Internal Server Error"
        },
    )

# ---------------------------------------------------------
# ROUTER REGISTRATION
# ---------------------------------------------------------
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(array.router)

# ---------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------

# Public root endpoint - Includes Real-Time DB Check for the Client
@app.get("/")
def root():
    # Attempt to connect to the DB right now to give the client a status report
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "Connected and Alive! "
    except Exception as e:
        db_status = f"Disconnected / Error  ({str(e)})"

    # Return the status to the terminal/browser
    return {
        "msg": "API is running",
        "database_status": db_status
    }

# Protected health endpoint - Requires valid JWT token
@app.get("/health")
def health(current_user = Depends(get_current_user)):
    return {"status": "ok", "user": current_user.username}