from sqlalchemy.orm import Session
from models import UserDB


class UserRepository:
    def __init__(self, db: Session):
        """
        The repository receives the database session once during initialization
        and stores it in self.db for use across all methods.
        """
        self.db = db

    def get_by_username(self, username: str) -> UserDB | None:
        """
        Fetch a single user by username.
        """
        # Use self.db instead of passing db as a parameter
        return self.db.query(UserDB).filter(UserDB.username == username).first()

    def create_user(self, username: str, password_hash: str, is_admin: bool) -> UserDB:
        """
        Create a new user in the database.
        """
        user = UserDB(
            username=username,
            password=password_hash,
            is_admin=is_admin
        )

        self.db.add(user)
        self.db.commit()
        return user

    def set_admin(self, username: str, is_admin: bool) -> UserDB | None:
        """
        Update the user's admin flag.
        """
        user = self.get_by_username(username)
        if not user:
            return None

        user.is_admin = is_admin
        self.db.commit()
        return user

    def list_users(self) -> list[UserDB]:
        """
        Return all users.
        """
        return self.db.query(UserDB).all()
