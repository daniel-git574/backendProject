"""
App-level configuration for auth and tokens.

Everything here is *static configuration*:
- cryptographic settings for JWTs (SECRET_KEY, ALGORITHM, EXPIRATION)
- an admin registration secret (ADMIN_SECRET)
- FastAPI's OAuth2 "where to get a token" declaration (oauth2_scheme)

NOW WITH ENV SUPPORT:
- You can override defaults via environment variables:
  SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_SECRET
"""

import os
from fastapi.security import OAuth2PasswordBearer

# ===== JWT & APP CONFIG =====
# Used to sign JWTs. In production, load from env var / secret manager.
# If not provided, fall back to a safe-but-static dev default.
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_TO_SOMETHING_RANDOM_AND_SECRET")

# JSON Web Token algorithm (HS256 = HMAC-SHA256 with SECRET_KEY).
ALGORITHM = "HS256"

# Default access-token lifetime (in minutes). Can be overridden by env.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# A one-time "admin registration secret".
# If a user provides this at registration time, they become an admin.
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "SUPER_ADMIN_SECRET")

# OAuth2PasswordBearer tells FastAPI to expect:
# Authorization: Bearer <token>
# And that the token is obtained via POST /login.
# (This affects docs + dependency resolution; it does NOT implement login.)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
