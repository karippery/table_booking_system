from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import (
    delete_user,
    get_user,
    get_user_by_email,
    create_user,
    update_user
    )
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserResponse,
    RefreshTokenRequest,
    UserUpdate
)
from app.utils.role import is_admin
from app.utils.security import (
    validate_email_format,
    verify_password,
    create_tokens,
    validate_password_strength
)
from app.utils.token import decode_token, get_current_user

router = APIRouter(tags=["auth"])


# create user
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        400: {"description": "Email already registered or invalid password"},
        500: {"description": "Internal server error"},
        201: {"description": "User created successfully"}
    }
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email and password.

    - **email**: must be unique and valid email format
    - **password**: must be at least 8 characters with
      uppercase, lowercase, and digits
    """
    try:
        # Check if email already registered
        validate_email_format(user.email)
        existing_user = await get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        validate_password_strength(user.password)

        new_user = await create_user(db=db, user=user)
        return new_user

    except HTTPException as http_ex:
        raise http_ex

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )


# Login user
@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Login with email and password",
    responses={
        401: {
            "description": "Authentication failed: Incorrect email or password"
        },
        403: {
            "description": "Account is inactive. Please contact support."
        },
        200: {
            "description": "Successfully logged in"
        }
    }
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access/refresh tokens.

    - **username**: User's email address
    - **password**: User's password
    """
    user = await get_user_by_email(db, email=form_data.username)
    validate_email_format(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: No account found with this email.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Incorrect password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Account is inactive. Please contact support or "
                "try again later."
            ),
        )

    access_token, refresh_token = create_tokens(user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# refresh token
@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    responses={
        401: {"description": "Invalid refresh token"},
        200: {"description": "New tokens generated"}
    }
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate new access token using refresh token.
    """
    try:
        payload = decode_token(token_data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user = await get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        access_token, refresh_token = create_tokens(user.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# Get current user details
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user details"
)
async def read_user_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user's details."""
    refreshed_user = await get_user(db, current_user.id)
    return refreshed_user


# get user by id (admin only)
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(is_admin)],
    summary="Update a user (Admin only)"
)
async def update_user_admin(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a user's information (Admin only)."""
    db_user = await get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return await update_user(db, db_user=db_user, user_update=user_update)


# delete user (admin only)
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(is_admin)],
    summary="Delete a user (Admin only)"
)
async def delete_user_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (Admin only)."""
    success = await delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
