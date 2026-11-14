# Backend entry point for Mother Theresa Transport Management System

import os
import secrets
import logging

# Configure basic logging (INFO level, timestamps) – safe for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import engine, Base, get_db
from backend.models import Owner
from backend.auth import hash_password
from backend.routers import (
    auth,
    dashboard,
    trucks,
    trips,
    expenses,
    drivers,
    salary,
    documents,
    reports,
    settings as settings_router,
)

# Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mother Theresa Transport Management System",
    description="Full-scale transport management system for Mother Theresa Transport",
    version="2.0.0",
)

# CORS middleware – allow all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# API routers (auth, CRUD, etc.)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# Front‑end static files
# -------------------------------------------------------------
frontend_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend"
)

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

# -------------------------------------------------------------
# Health check endpoint
# -------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
    }

# -------------------------------------------------------------
# Request model for owner reset (protected)
# -------------------------------------------------------------
class OwnerResetRequest(BaseModel):
    username: str
    password: str
    full_name: str = "Transport Owner"

# -------------------------------------------------------------
# Protected diagnostic endpoint (temporary, bootstrap‑key protected)
# -------------------------------------------------------------
@app.post("/api/admin/diagnostics")
def diagnostics(
    bootstrap_key: str = Header(default="", alias="X-Bootstrap-Key"),
    db: Session = Depends(get_db),
):
    """Return minimal diagnostic information about the authentication DB and Owner.
    No secrets, passwords, hashes or tokens are exposed.
    """
    required_key = os.getenv("OWNER_BOOTSTRAP_KEY")
    if not required_key or not secrets.compare_digest(bootstrap_key, required_key):
        raise HTTPException(status_code=403, detail="Access denied")

    db_path = None
    if settings.DATABASE_URL.startswith("sqlite"):
        db_path = settings.DATABASE_URL.split("///")[-1]
    owner = db.query(Owner).order_by(Owner.id.asc()).first()
    return {
        "database_path": db_path,
        "owner_exists": bool(owner),
        "owner_active": owner.is_active if owner else False,
    }


# -------------------------------------------------------------
# Protected reset‑owner endpoint (identical to original behavior)
# -------------------------------------------------------------
@app.post("/api/admin/reset-owner")
def reset_owner(
    payload: OwnerResetRequest,
    bootstrap_key: str = Header(default="", alias="X-Bootstrap-Key"),
    db: Session = Depends(get_db),
):
    required_key = os.getenv("OWNER_BOOTSTRAP_KEY")
    if not required_key or not secrets.compare_digest(bootstrap_key, required_key):
        raise HTTPException(status_code=403, detail="Access denied")

    username = payload.username.strip()
    password = payload.password

    # Validate credentials (minimum security constraints)
    if not username or len(password) < 8 or len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    owner = db.query(Owner).order_by(Owner.id.asc()).first()
    if owner:
        owner.username = username
        owner.hashed_password = hash_password(password)
        owner.full_name = payload.full_name
        owner.is_active = True
        action = "updated"
    else:
        owner = Owner(
            username=username,
            hashed_password=hash_password(password),
            full_name=payload.full_name,
            is_active=True,
        )
        db.add(owner)
        action = "created"
    db.commit()
    return {
        "success": True,
        "message": f"Owner account {action} successfully",
        "username": username,
    }
