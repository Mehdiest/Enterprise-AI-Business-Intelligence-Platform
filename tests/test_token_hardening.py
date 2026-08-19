"""Regression tests for token hardening and SQL read-only enforcement."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import settings
from app.dependencies.auth import _token_subject
from app.services.ai.copilot.agents.sql.validator import SQLValidator
from app.services.auth import AuthService


def _decode(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def test_access_token_is_typed_as_access():
    token = AuthService.create_access_token({"sub": "user-1"})

    assert _decode(token)["type"] == "access"
    assert _token_subject(token) == "user-1"


def test_refresh_token_is_rejected_as_access_token():
    refresh_token = AuthService.create_refresh_token({"sub": "user-1"})

    with pytest.raises(HTTPException) as error:
        _token_subject(refresh_token)

    assert error.value.status_code == 401


def test_refresh_token_carries_unique_jti():
    first = AuthService.create_refresh_token({"sub": "user-1"})
    second = AuthService.create_refresh_token({"sub": "user-1"})

    assert _decode(first)["jti"] != _decode(second)["jti"]


def test_refresh_token_without_jti_is_invalid():
    token = jwt.encode(
        {"sub": "user-1", "type": "refresh"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    assert AuthService._decode_refresh_token(token) is None


def test_tampered_refresh_token_is_invalid():
    token = AuthService.create_refresh_token({"sub": "user-1"})

    assert AuthService._decode_refresh_token(token + "x") is None


def test_validator_allows_select():
    SQLValidator().validate("SELECT customer_name FROM dim_customer")


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM dim_customer",
        "SELECT 1; DROP TABLE dim_customer",
        "SELECT 1 FROM dim_customer WHERE 1=1 UNION SELECT 1; TRUNCATE fact_sales",
    ],
)
def test_validator_rejects_write_statements(sql):
    with pytest.raises(ValueError):
        SQLValidator().validate(sql)


def test_validator_rejects_empty_query():
    with pytest.raises(ValueError):
        SQLValidator().validate("   ")
