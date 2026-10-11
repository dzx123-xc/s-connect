from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.routes.admin import router as admin_router

__all__ = ["auth_router", "health_router", "admin_router"]