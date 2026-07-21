from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = _token_subject(token)
    current_user = await _find_user(db, user_id)
    if current_user is None or not current_user.is_active:
        raise _credentials_exception()
    return current_user


def _token_subject(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise _credentials_exception() from None
    user_id = payload.get("sub")
    if user_id is None:
        raise _credentials_exception()
    return user_id


async def _find_user(db: AsyncSession, user_id: str) -> User | None:
    query_result = await db.execute(select(User).where(User.id == user_id))
    return query_result.scalar_one_or_none()


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
