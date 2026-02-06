"""
Simple verification script for JWT authentication implementation.

This script tests the JWT verification logic without requiring a running server.
It generates a test JWT token and verifies it using the same logic as the API.
"""

import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional


# Duplicate the classes from jwt_handler.py for standalone testing
class TokenData(BaseModel):
    """Validated token data extracted from JWT payload."""
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
    """Verify JWT token signature and extract user identity."""
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub", "exp"]
            }
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise TokenInvalidError("Missing 'sub' claim in token payload")

        user_id_str = str(user_id)
        email = payload.get("email")
        iat = payload.get("iat")
        exp = payload.get("exp")

        issued_at = datetime.fromtimestamp(iat) if iat else None
        expires_at = datetime.fromtimestamp(exp) if exp else None

        return TokenData(
            user_id=user_id_str,
            email=email,
            issued_at=issued_at,
            expires_at=expires_at
        )

    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError(
            "JWT token has expired. Please sign in again."
        ) from e

    except jwt.InvalidTokenError as e:
        raise TokenInvalidError(
            f"Invalid JWT token: {str(e)}"
        ) from e

    except Exception as e:
        raise TokenInvalidError(
            f"JWT verification failed: {str(e)}"
        ) from e


def test_jwt_verification():
    """Test JWT verification with valid, expired, and invalid tokens."""

    # Test secret (same as would be in BETTER_AUTH_SECRET)
    test_secret = "test_secret_key_for_jwt_verification_minimum_32_chars"

    print("=" * 70)
    print("JWT Verification Test Suite")
    print("=" * 70)

    # Test 1: Valid token
    print("\n[TEST 1] Valid JWT Token")
    print("-" * 70)

    valid_payload = {
        "sub": "123",  # user_id
        "email": "user@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    valid_token = jwt.encode(valid_payload, test_secret, algorithm="HS256")
    print(f"Generated token: {valid_token[:50]}...")

    try:
        token_data = verify_jwt_token(valid_token, test_secret)
        print(f"[PASS] Token verified successfully")
        print(f"  - User ID: {token_data.user_id}")
        print(f"  - Email: {token_data.email}")
        print(f"  - Issued at: {token_data.issued_at}")
        print(f"  - Expires at: {token_data.expires_at}")
    except Exception as e:
        print(f"[FAIL] Verification failed: {e}")
        return False

    # Test 2: Expired token
    print("\n[TEST 2] Expired JWT Token")
    print("-" * 70)

    expired_payload = {
        "sub": "456",
        "email": "expired@example.com",
        "iat": datetime.utcnow() - timedelta(hours=48),
        "exp": datetime.utcnow() - timedelta(hours=24)  # Expired 24 hours ago
    }

    expired_token = jwt.encode(expired_payload, test_secret, algorithm="HS256")
    print(f"Generated expired token: {expired_token[:50]}...")

    try:
        token_data = verify_jwt_token(expired_token, test_secret)
        print(f"[FAIL] Token should have been rejected (expired)")
        return False
    except TokenExpiredError as e:
        print(f"[PASS] Token correctly rejected as expired")
        print(f"  - Error: {str(e)}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

    # Test 3: Invalid signature
    print("\n[TEST 3] Invalid Signature")
    print("-" * 70)

    # Create token with one secret, try to verify with another
    wrong_secret = "wrong_secret_key_this_will_fail_signature_verification"
    invalid_token = jwt.encode(valid_payload, wrong_secret, algorithm="HS256")
    print(f"Generated token with wrong secret: {invalid_token[:50]}...")

    try:
        token_data = verify_jwt_token(invalid_token, test_secret)
        print(f"[FAIL] Token should have been rejected (invalid signature)")
        return False
    except TokenInvalidError as e:
        print(f"[PASS] Token correctly rejected (invalid signature)")
        print(f"  - Error: {str(e)}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

    # Test 4: Missing sub claim
    print("\n[TEST 4] Missing 'sub' Claim")
    print("-" * 70)

    missing_sub_payload = {
        "email": "nosubclaim@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    missing_sub_token = jwt.encode(missing_sub_payload, test_secret, algorithm="HS256")
    print(f"Generated token without 'sub': {missing_sub_token[:50]}...")

    try:
        token_data = verify_jwt_token(missing_sub_token, test_secret)
        print(f"[FAIL] Token should have been rejected (missing sub claim)")
        return False
    except TokenInvalidError as e:
        print(f"✓ Token correctly rejected (missing 'sub' claim)")
        print(f"  - Error: {str(e)}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

    # Test 5: Malformed token
    print("\n[TEST 5] Malformed Token")
    print("-" * 70)

    malformed_token = "not.a.valid.jwt.token"
    print(f"Malformed token: {malformed_token}")

    try:
        token_data = verify_jwt_token(malformed_token, test_secret)
        print(f"✗ Token should have been rejected (malformed)")
        return False
    except TokenInvalidError as e:
        print(f"✓ Token correctly rejected (malformed)")
        print(f"  - Error: {str(e)}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

    # All tests passed
    print("\n" + "=" * 70)
    print("✓ All JWT verification tests passed!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    import sys
    success = test_jwt_verification()
    sys.exit(0 if success else 1)
