from fastapi import HTTPException, status, Depends
from app.models.user import User, UserRole
from app.utils.token import get_current_user


def is_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify current user has admin privileges
    Raises 403 Forbidden if not admin
    Returns the authenticated admin user
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


def is_guest(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify current user has guest or admin privileges
    Raises 403 Forbidden if neither guest nor admin
    Returns the authenticated user
    """
    if current_user.role not in (UserRole.GUEST, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest or Admin privileges required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user
