"""
FastAPI main application for Todo API.
Includes CORS configuration, router registration, and OpenAPI documentation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router
from src.api.chat import router as chat_router

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Multi-user Todo API with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Todo API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check for monitoring."""
    return {"status": "healthy"}


# Register routers
app.include_router(auth_router)  # Auth endpoints: /api/auth/signup, /api/auth/signin
app.include_router(tasks_router)  # Task endpoints: /api/tasks
app.include_router(chat_router)  # Chat endpoints: /api/chat (Phase III)
