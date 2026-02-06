"""
JWT token verification module for FastAPI authentication.

This module provides secure JWT token verification using PyJWT library.
Tokens are issued by Better Auth (Next.js) and verified by the FastAPI backend
using a shared BETTER_AUTH_SECRET.

Security Features:
- HS256 algorithm (HMAC with SHA-256)
- Signature verification with shared secret
- Expiration validation (exp claim)
- User identity extraction from 'sub' claim (JWT standard)
- Comprehensive error handling for expired and invalid tokens

Token Structure:
  Header.Payload.Signature

Expected Claims:
  - sub: User ID (primary identifier)
  - iat: Issued at timestamp
  - exp: Expiration timestamp
  - email: Optional user email
"""

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TokenData(BaseModel):
    """
    Validated token data extracted from JWT payload.

    Attributes:
        user_id: User identifier extracted from 'sub' claim
        email: Optional user email from custom claim
        issued_at: Token issuance timestamp
        expires_at: Token expiration timestamp
    """
    user_id: str = Field(..., description="User identifier from 'sub' claim")
    email: Optional[str] = Field(None, description="User email address")
    issued_at: Optional[datetime] = Field(None, description="Token issuance time")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")


class JWTVerificationError(Exception):
    """Base exception for JWT verification failures."""
    pass


class TokenExpiredError(JWTVerificationError):
    """Raised when JWT token has expired."""
    pass


class TokenInvalidError(JWTVerificationError):
    """Raised when JWT token signature or structure is invalid."""
    pass


def verify_jwt_token(token: str, secret_key: str, algorithm: str = "HS256") -> TokenData:
    """
    Verify JWT token signature and extract user identity.

    This function performs comprehensive JWT verification:
    1. Validates token signature using shared secret
    2. Checks token expiration (exp claim)
    3. Extracts user_id from 'sub' claim (JWT standard)
    4. Returns structured TokenData with user identity

    Security Guarantees:
    - Signature verification prevents token tampering
    - Expiration check prevents replay attacks with old tokens
    - Algorithm enforcement prevents algorithm confusion attacks
    - No user identity returned without successful verification

    Args:
        token: JWT token string (format: Header.Payload.Signature)
        secret_key: Shared secret for signature verification (BETTER_AUTH_SECRET)
        algorithm: JWT signing algorithm (default: HS256)

    Returns:
        TokenData: Validated token data with user_id and optional email

    Raises:
        TokenExpiredError: When token has expired (exp claim in past)
        TokenInvalidError: When signature invalid, missing claims, or malformed token

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> secret = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
        >>> token_data = verify_jwt_token(token, secret)
        >>> print(token_data.user_id)
        "123"

    Security Notes:
        - Always use the same secret_key as Better Auth (Next.js)
        - Never log or expose the secret_key
        - Token verification must happen on every authenticated request
        - Frontend tokens are untrusted until backend verification succeeds
    """
    try:
        # Decode and verify JWT token
        # - Verifies signature matches secret_key
        # - Validates exp (expiration) claim automatically
        # - Validates nbf (not before) claim if present
        # - Returns decoded payload as dictionary
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            options={
                "verify_signature": True,  # Verify HMAC signature
                "verify_exp": True,        # Verify expiration time
                "require": ["sub", "exp"]  # Require critical claims
            }
        )

        # Extract user_id from 'sub' claim (JWT standard for subject/user identifier)
        user_id = payload.get("sub")
        if user_id is None:
            raise TokenInvalidError("Missing 'sub' claim in token payload")

        # Convert user_id to string for consistency (may be int or str in token)
        user_id_str = str(user_id)

        # Extract optional email claim
        email = payload.get("email")

        # Extract timestamp claims for debugging/logging
        iat = payload.get("iat")
        exp = payload.get("exp")

        # Convert Unix timestamps to datetime objects
        issued_at = datetime.fromtimestamp(iat) if iat else None
        expires_at = datetime.fromtimestamp(exp) if exp else None

        return TokenData(
            user_id=user_id_str,
            email=email,
            issued_at=issued_at,
            expires_at=expires_at
        )

    except ExpiredSignatureError as e:
        # Token expiration is a security control, not an error condition
        # User must re-authenticate to obtain a fresh token
        raise TokenExpiredError(
            "JWT token has expired. Please sign in again."
        ) from e

    except InvalidTokenError as e:
        # Catch all other JWT errors (invalid signature, malformed token, etc.)
        # These indicate potential tampering or misconfiguration
        raise TokenInvalidError(
            f"Invalid JWT token: {str(e)}"
        ) from e

    except Exception as e:
        # Unexpected errors should fail closed (deny access)
        raise TokenInvalidError(
            f"JWT verification failed: {str(e)}"
        ) from e


def extract_token_from_header(authorization_header: str) -> str:
    """
    Extract JWT token from Authorization header.

    Expected format: "Bearer <token>"

    Args:
        authorization_header: Raw Authorization header value

    Returns:
        str: Extracted JWT token

    Raises:
        TokenInvalidError: If header format is invalid

    Example:
        >>> header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> token = extract_token_from_header(header)
        >>> print(token)
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if not authorization_header:
        raise TokenInvalidError("Missing Authorization header")

    parts = authorization_header.split()

    if len(parts) != 2:
        raise TokenInvalidError(
            "Invalid Authorization header format. Expected: 'Bearer <token>'"
        )

    scheme, token = parts

    if scheme.lower() != "bearer":
        raise TokenInvalidError(
            f"Invalid authentication scheme: {scheme}. Expected: 'Bearer'"
        )

    return token
