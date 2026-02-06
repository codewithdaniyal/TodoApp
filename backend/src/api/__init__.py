"""
FastAPI routers package for Todo API endpoints.
"""

from .tasks import router as tasks_router

__all__ = ["tasks_router"]
