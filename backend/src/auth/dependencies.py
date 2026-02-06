"""
FastAPI authentication dependencies for JWT verification.

This module provides dependency injection functions for route protection.
All protected routes inject get_current_user() via Depends() to enforce
authentication and extract user identity from JWT tokens.

Usage in Routes:
    from fastapi import Depends
    from auth.dependencies import get_current_user

    @router.get("/tasks")
    async def get_tasks(current_user: TokenData = Depends(get_current_user)):
        user_id = current_user.user_id
        # Query tasks filtered by user_id...

Security Architecture:
- OAuth2PasswordBearer extracts token from Authorization header
- Token verification uses shared BETTER_AUTH_SECRET
- Invalid/expired tokens return 401 Unauthorized automatically
- User identity extracted once per request via dependency injection
- All data queries must filter by current_user.user_id for isolation

HTTP Status Codes:
- 401 Unauthorized: Missing, invalid, or expired JWT token
- 403 Forbidden: Valid token but insufficient permissions (resource ownership)
- 200 OK: Successful authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from .jwt_handler import (
    verify_jwt_token,
    TokenData,
    TokenExpiredError,
    TokenInvalidError
)
from ..config import settings


# OAuth2PasswordBearer scheme for Authorization header extraction
# tokenUrl parameter is required but not used (Better Auth handles token issuance)
# This scheme automatically:
# - Extracts "Authorization: Bearer <token>" header
# - Returns token string to dependency function
# - Returns 401 if Authorization header is missing
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",  # Required parameter (not used in our architecture)
    scheme_name="JWT",
    description="JWT token issued by Better Auth"
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> TokenData:
    """
    FastAPI dependency for extracting and validating current user from JWT.

    This dependency should be injected into all protected route handlers to:
    1. Extract JWT token from Authorization header
    2. Verify token signature and expiration
    3. Extract user identity (user_id, email)
    4. Return validated TokenData for use in route handler

    Security Enforcement:
    - Called on every request to protected endpoints
    - Fails fast with 401 for invalid/missing/expired tokens
    - No route handler code executes without successful verification
    - User identity is cryptographically verified (signature check)

    Args:
        token: JWT token string extracted from Authorization header by oauth2_scheme

    Returns:
        TokenData: Validated token data containing user_id and optional email

    Raises:
        HTTPException(401): When token is missing, invalid, expired, or malformed

    Usage Example:
        @router.get("/tasks")
        async def get_user_tasks(
            current_user: TokenData = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            # User is authenticated at this point
            user_id = current_user.user_id

            # Query tasks with user isolation
            statement = select(Task).where(Task.user_id == user_id)
            tasks = db.exec(statement).all()

            return {"tasks": tasks}

    Security Notes:
        - This dependency runs before route handler logic
        - Route handlers receive validated user identity
        - Database queries MUST filter by current_user.user_id
        - Never trust user_id from request body/query params
        - Always use current_user.user_id from verified JWT
    """
    # Credentials exception for all authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify JWT token signature and extract user identity
        # - Validates signature with BETTER_AUTH_SECRET
        # - Checks expiration (exp claim)
        # - Extracts user_id from 'sub' claim
        token_data = verify_jwt_token(
            token=token,
            secret_key=settings.better_auth_secret,
            algorithm=settings.jwt_algorithm
        )

        # Additional validation: Ensure user_id is present and non-empty
        if not token_data.user_id:
            raise credentials_exception

        return token_data

    except TokenExpiredError:
        # Token expiration requires re-authentication
        # Frontend should clear token and redirect to signin
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except TokenInvalidError as e:
        # Invalid token indicates tampering or misconfiguration
        # Return generic error message to avoid information disclosure
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        # Unexpected errors fail closed (deny access)
        # Log error for debugging but return generic message to client
        # TODO: Add structured logging for security audit trail
        raise credentials_exception


async def get_current_user_id(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> str:
    """
    Convenience dependency that returns only the user_id string.

    Use this when you only need the user_id and don't need email or other token data.

    Args:
        current_user: Validated TokenData from get_current_user dependency

    Returns:
        str: User identifier from JWT 'sub' claim

    Usage Example:
        @router.delete("/tasks/{task_id}")
        async def delete_task(
            task_id: int,
            user_id: str = Depends(get_current_user_id),
            db: Session = Depends(get_db)
        ):
            # Verify ownership before deletion
            task = db.get(Task, task_id)
            if not task or task.user_id != user_id:
                raise HTTPException(status_code=404, detail="Task not found")

            db.delete(task)
            db.commit()
            return {"message": "Task deleted"}
    """
    return current_user.user_id


# Type aliases for dependency injection annotations
# These provide clear, self-documenting route handler signatures

# Full token data (user_id, email, timestamps)
CurrentUser = Annotated[TokenData, Depends(get_current_user)]

# Just the user_id string
CurrentUserId = Annotated[str, Depends(get_current_user_id)]


# Example usage patterns for route handlers:

"""
PATTERN 1: Full token data (when you need email or timestamps)
-----------------------------------------------------------------

from auth.dependencies import CurrentUser

@router.get("/profile")
async def get_profile(current_user: CurrentUser):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "token_issued_at": current_user.issued_at
    }


PATTERN 2: User ID only (most common for data queries)
-----------------------------------------------------------------

from auth.dependencies import CurrentUserId

@router.get("/tasks")
async def get_tasks(user_id: CurrentUserId, db: Session = Depends(get_db)):
    statement = select(Task).where(Task.user_id == user_id)
    tasks = db.exec(statement).all()
    return {"tasks": tasks}


PATTERN 3: Explicit dependency injection (most readable)
-----------------------------------------------------------------

from auth.dependencies import get_current_user
from fastapi import Depends

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = Task(
        title=task_data.title,
        user_id=current_user.user_id  # Enforce ownership
    )
    db.add(task)
    db.commit()
    return task


ANTI-PATTERNS (DO NOT USE):
-----------------------------------------------------------------

# ❌ NEVER trust user_id from request body
@router.get("/tasks")
async def get_tasks(user_id: int):  # Vulnerable to authorization bypass!
    # Attacker can pass any user_id to access other users' tasks
    ...

# ❌ NEVER skip authentication dependency
@router.get("/tasks")
async def get_tasks():
    # No authentication - anyone can access this endpoint
    ...

# ❌ NEVER filter by request-provided user_id
@router.get("/tasks")
async def get_tasks(
    request_user_id: int,  # From query params or body
    current_user: CurrentUser
):
    # Using request_user_id instead of current_user.user_id
    statement = select(Task).where(Task.user_id == request_user_id)  # ❌ INSECURE
    ...


SECURE PATTERN (ALWAYS USE):
-----------------------------------------------------------------

@router.get("/tasks")
async def get_tasks(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ✅ ALWAYS use current_user.user_id from verified JWT
    user_id = current_user.user_id

    # ✅ ALWAYS filter queries by authenticated user_id
    statement = select(Task).where(Task.user_id == user_id)
    tasks = db.exec(statement).all()

    return {"tasks": tasks}


OWNERSHIP VALIDATION PATTERN:
-----------------------------------------------------------------

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ✅ Query with user_id filter to enforce ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.user_id  # Ownership check
    )
    task = db.exec(statement).first()

    # Return 404 (not 403) to avoid information disclosure
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Update task fields
    task.title = task_update.title
    task.completed = task_update.completed
    db.add(task)
    db.commit()
    db.refresh(task)

    return task
"""
