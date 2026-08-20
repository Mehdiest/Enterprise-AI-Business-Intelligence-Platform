"""
Role-Based Access Control (RBAC) dependencies.
"""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User


class RoleRequired:
    """
    FastAPI dependency for enforcing role-based access.
    """

    def __init__(
        self,
        allowed_roles: Sequence[str],
    ):
        self.allowed_roles = {
            role.lower().strip()
            for role in allowed_roles
        }

    def __call__(
        self,
        current_user: User = Depends(
            get_current_user,
        ),
    ) -> User:
        """
        Validate the current user's role.
        """

        user_role = (
            current_user.role or ""
        ).lower().strip()

        if user_role not in self.allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user


# ==========================================================
# Common role dependencies
# ==========================================================
#
# Role hierarchy (most to least privileged): admin > analyst > viewer.
# Each dependency lists every role permitted at or above its access tier.

require_admin = RoleRequired(
    [
        "admin",
    ]
)

require_analyst = RoleRequired(
    [
        "admin",
        "analyst",
    ]
)

require_viewer = RoleRequired(
    [
        "admin",
        "analyst",
        "viewer",
    ]
)

