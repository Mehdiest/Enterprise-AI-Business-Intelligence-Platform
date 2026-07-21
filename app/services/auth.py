"""
Authentication service.
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        db: AsyncSession,
    ):
        self.db = db

    async def register(
        self,
        request: RegisterRequest,
    ) -> User:

        existing = (
            await self.db.execute(select(User).where(User.email == request.email))
        ).scalar_one_or_none()

        if existing:
            raise ValueError("Email already exists.")

        user = User(
            full_name=request.full_name,
            email=request.email,
            hashed_password=pwd_context.hash(request.password),
            role="viewer",
            is_active=True,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def login(self, email: str, password: str) -> dict | None:
        user = await self._find_user_by_email(email)
        if user is None or not self._password_matches(password, user):
            return None
        return self._token_pair(user)

    async def refresh_access_token(self, refresh_token: str) -> dict | None:
        user_id = self._refresh_subject(refresh_token)
        if user_id is None:
            return None
        user = await self._find_user_by_id(user_id)
        if user is None:
            return None
        return self._token_pair(user, refresh_token)

    async def _find_user_by_email(self, email: str) -> User | None:
        query_result = await self.db.execute(select(User).where(User.email == email))
        return query_result.scalar_one_or_none()

    async def _find_user_by_id(self, user_id: str) -> User | None:
        query_result = await self.db.execute(select(User).where(User.id == user_id))
        return query_result.scalar_one_or_none()

    @staticmethod
    def _password_matches(password: str, user: User) -> bool:
        return pwd_context.verify(password, user.hashed_password)

    def _token_pair(self, user: User, refresh_token: str | None = None) -> dict:
        token_subject = {"sub": str(user.id)}
        return {
            "access_token": self.create_access_token(token_subject),
            "refresh_token": refresh_token or self.create_refresh_token(token_subject),
            "token_type": "bearer",
        }

    @staticmethod
    def _refresh_subject(refresh_token: str) -> str | None:
        try:
            payload = jwt.decode(
                refresh_token, settings.secret_key, algorithms=[settings.algorithm]
            )
        except JWTError:
            return None
        return payload.get("sub") if payload.get("type") == "refresh" else None

    @staticmethod
    def create_access_token(
        data: dict,
    ) -> str:

        payload = data.copy()

        expire = datetime.now(UTC) + timedelta(
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

        expire = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days,
        )

        payload["exp"] = expire
        payload["type"] = "refresh"

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )
