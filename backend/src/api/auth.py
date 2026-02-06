"""
Authentication API endpoints for user signup and signin.
Issues JWT tokens for authenticated access.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt

from ..database import get_session
from ..models.user import User
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    """User registration request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    name: Optional[str] = Field(None, description="User display name")


class SigninRequest(BaseModel):
    """User authentication request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Authentication response with user data and JWT token."""
    data: dict
    message: str


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    # Convert password to bytes and generate salt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_jwt_token(user_id: int, email: str) -> str:
    """
    Create JWT token with user claims.

    Args:
        user_id: User identifier
        email: User email address

    Returns:
        JWT token string
    """
    payload = {
        "sub": str(user_id),  # JWT standard: subject claim
        "email": email,
        "iat": datetime.utcnow(),  # Issued at
        "exp": datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm
    )

    return token


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Register new user account and issue JWT token.

    Validates:
    - Email format and uniqueness
    - Password minimum length (8 characters)

    Returns:
    - 201 Created: User account created successfully with JWT token
    - 422 Unprocessable Entity: Email already exists or validation error
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == signup_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(signup_data.password)

    # Create new user
    new_user = User(
        email=signup_data.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    token = create_jwt_token(new_user.id, new_user.email)

    return AuthResponse(
        data={
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "created_at": new_user.created_at.isoformat()
            },
            "token": token,
            "expires_at": (datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)).isoformat()
        },
        message="Account created successfully"
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    signin_data: SigninRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and issue JWT token.

    Validates:
    - Email and password match existing user

    Returns:
    - 200 OK: Authentication successful with JWT token
    - 401 Unauthorized: Invalid email or password
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == signin_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(signin_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_jwt_token(user.id, user.email)

    return AuthResponse(
        data={
            "user": {
                "id": user.id,
                "email": user.email
            },
            "token": token,
            "expires_at": (datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)).isoformat()
        },
        message="Signed in successfully"
    )
