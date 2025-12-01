from pydantic import BaseModel

class RegisterRequest(BaseModel):
    # The username to create (must be unique in DB).
    username: str
    # Plain password for the exercise (no hashing here).
    password: str
    # Optional secret that, if correct, registers the user as admin.
    admin_secret: str | None = None

class UserOut(BaseModel):
    # Public view of a user (no password here!).
    username: str
    # Whether this user is an admin (authorization decisions on server).
    is_admin: bool
    # If you later add created_at to the SQLAlchemy model, you can also expose it here.

    class Config:
        # Allow Pydantic to build this model directly from SQLAlchemy objects
        # (it reads attributes instead of expecting dicts).
        from_attributes = True