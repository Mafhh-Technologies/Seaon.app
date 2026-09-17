"""
Role-based access control dependencies.
"""
from fastapi import Depends, HTTPException, status

from app.core.security import decode_access_token
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session


def get_current_user(
    token: str = Depends(lambda: None),  # replaced below via Header
    db: Session = Depends(get_db),
) -> User:
    """
    Placeholder — actual implementation lives in routes/auth.py.
    This exists so permissions are importable and overridable.
    """
    raise NotImplementedError


def require_roles(*allowed_roles: str):
    """
    Factory that returns a dependency requiring the current user to have
    one of the provided roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles("admin"))])
    """
    from app.api.routes.auth import get_current_active_user

    def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}",
            )
        return current_user

    return _checker