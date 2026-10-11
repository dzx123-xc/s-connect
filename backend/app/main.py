from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.database import init_db, SessionLocal
from app.routes import auth_router, health_router, admin_router
from app.auth.session import SessionMiddleware
from app.services.location_service import seed_locations
from app.services.admin_service import bootstrap_admin_from_env


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_locations(db)
        bootstrap_admin_from_env(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
frontend_dir = os.path.abspath(frontend_dir)

if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "SConnect API", "version": settings.app_version}

    @app.get("/{page}.html")
    async def serve_html(page: str):
        allowed_pages = {
            "index", "discover", "player-dashboard", "coach-dashboard",
            "club-dashboard", "organizer-dashboard", "referee-dashboard", "admin-portal"
        }
        if page not in allowed_pages:
            return {"detail": "Page not found"}
        file_path = os.path.join(frontend_dir, f"{page}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return {"detail": "Page not found"}
else:
    @app.get("/")
    async def root():
        return {"message": "SConnect API", "version": settings.app_version, "frontend": "not built"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)