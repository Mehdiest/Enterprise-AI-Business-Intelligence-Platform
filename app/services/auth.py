"""Authenticate users and issue rotating JWT token pairs."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

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
    """Authenticate users and manage their active refresh token."""

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
        if user is None or not user.is_active:
            return None
        if not self._password_matches(password, user):
            return None
        return await self._token_pair(user)

    async def refresh_access_token(self, refresh_token: str) -> dict | None:
        payload = self._decode_refresh_token(refresh_token)
        if payload is None:
            return None
        user = await self._find_user_by_id(payload["sub"])
        if user is None or not user.is_active:
            return None
        if user.refresh_token_jti != payload["jti"]:
            return None
        if user.refresh_token_hash != self._token_hash(refresh_token):
            return None
        return await self._token_pair(user)

    async def _find_user_by_email(self, email: str) -> User | None:
        query_result = await self.db.execute(select(User).where(User.email == email))
        return query_result.scalar_one_or_none()

    async def _find_user_by_id(self, user_id: str) -> User | None:
        query_result = await self.db.execute(select(User).where(User.id == user_id))
        return query_result.scalar_one_or_none()

    @staticmethod
    def _password_matches(password: str, user: User) -> bool:
        return pwd_context.verify(password, user.hashed_password)

    async def _token_pair(self, user: User) -> dict:
        subject = {"sub": str(user.id)}
        jti = str(uuid4())
        refresh_token = self.create_refresh_token(subject, jti)
        user.refresh_token_jti = jti
        user.refresh_token_hash = self._token_hash(refresh_token)
        await self.db.commit()
        return {
            "access_token": self.create_access_token(subject),
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def _decode_refresh_token(refresh_token: str) -> dict | None:
        try:
            payload = jwt.decode(
                refresh_token, settings.secret_key, algorithms=[settings.algorithm]
            )
        except JWTError:
            return None
        required_claims = (payload.get("sub"), payload.get("jti"))
        if payload.get("type") != "refresh" or not all(required_claims):
            return None
        return payload

    @staticmethod
    def _token_hash(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

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
        jti: str | None = None,
    ) -> str:

        payload = data.copy()

        expire = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days,
        )

        payload["exp"] = expire
        payload["type"] = "refresh"
        payload["jti"] = jti or str(uuid4())

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )
