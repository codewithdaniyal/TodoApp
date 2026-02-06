"""
Authentication module for JWT verification and user identity management.

This module provides secure JWT authentication for the FastAPI backend.
Tokens are issued by Better Auth (Next.js) and verified using a shared secret.

Public API:
    Dependencies:
        - get_current_user: Extract and verify user from JWT (returns TokenData)
        - get_current_user_id: Extract and verify user_id only (returns str)
        - CurrentUser: Type annotation for TokenData dependency
        - CurrentUserId: Type annotation for user_id dependency

    JWT Handler:
        - verify_jwt_token: Low-level JWT verification function
        - TokenData: Pydantic model for validated token data
        - TokenExpiredError: Exception for expired tokens
        - TokenInvalidError: Exception for invalid tokens

Usage:
    from auth import get_current_user, CurrentUser

    @router.get("/protected")
    async def protected_route(current_user: CurrentUser):
        return {"user_id": current_user.user_id}
"""

from .dependencies import (
    get_current_user,
    get_current_user_id,
    CurrentUser,
    CurrentUserId,
)

from .jwt_handler import (
    verify_jwt_token,
    TokenData,
    TokenExpiredError,
    TokenInvalidError,
)

__all__ = [
    # Dependencies for route protection
    "get_current_user",
    "get_current_user_id",
    "CurrentUser",
    "CurrentUserId",
    # JWT verification utilities
    "verify_jwt_token",
    "TokenData",
    "TokenExpiredError",
    "TokenInvalidError",
]
