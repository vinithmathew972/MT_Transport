import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import engine, Base, get_db
from backend.seed import seed_database
from backend.routers import auth, dashboard, trucks, trips, expenses, drivers, salary, documents, reports, settings as settings_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mother Theresa Transport Management System",
    description="Full-scale transport management system for Mother Theresa Transport",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto seed on application launch
# Automatic seeding disabled to prevent demo data recreation on app restart.
# To seed manually, run `python -m backend.seed`.
# Include API Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(trucks.router)
app.include_router(trips.router)
app.include_router(expenses.router)
app.include_router(drivers.router)
app.include_router(salary.router)
app.include_router(documents.router)
app.include_router(reports.router)
app.include_router(settings_router.router)

# Mount frontend static directory
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_landing_page():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    @app.get("/login")
    def serve_login_page():
        return FileResponse(os.path.join(frontend_dir, "login.html"))

    @app.get("/dashboard")
    def serve_dashboard_page():
        return FileResponse(os.path.join(frontend_dir, "dashboard.html"))

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE
    }
