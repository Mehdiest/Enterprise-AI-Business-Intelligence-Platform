"""
Authentication service.
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import JWTError
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.schemas.auth import RegisterRequest


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class AuthService:
    """
    Authentication service.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def register(
        self,
        request: RegisterRequest,
    ) -> User:

        existing = (
            self.db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if existing:
            raise ValueError("Email already exists.")

        user = User(
            full_name=request.full_name,
            email=request.email,
            hashed_password=pwd_context.hash(
                request.password
            ),
            role="viewer",
            is_active=True,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login(
        self,
        email: str,
        password: str,
    ):

        user = (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user is None:
            return None

        if not pwd_context.verify(
            password,
            user.hashed_password,
        ):
            return None

        access_token = self.create_access_token(
            {
                "sub": str(user.id),
            }
        )

        refresh_token = self.create_refresh_token(
            {
                "sub": str(user.id),
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_access_token(
        self,
        refresh_token: str,
    ):

        try:
            payload = jwt.decode(
                refresh_token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
        except JWTError:
            return None

        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")

        if user_id is None:
            return None

        user = (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return None

        access_token = self.create_access_token(
            {
                "sub": str(user.id),
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def create_access_token(
        data: dict,
    ) -> str:

        payload = data.copy()

        expire = datetime.now(
            timezone.utc
        ) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )

        payload["exp"] = expire
        payload["type"] = "access"

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    @staticmethod
    def create_refresh_token(
        data: dict,
    ) -> str:

        payload = data.copy()

        expire = datetime.now(
            timezone.utc
        ) + timedelta(
            days=settings.refresh_token_expire_days,
        )

        payload["exp"] = expire
        payload["type"] = "refresh"

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )