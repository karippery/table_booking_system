from fastapi import HTTPException, status, Depends
from app.models.user import User, UserRole
from app.utils.token import get_current_user


def is_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def is_guest(current_user: User = Depends(get_current_user)):
    if current_user.role not in (UserRole.GUEST, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest or Admin privileges required",
        )
    return current_user
