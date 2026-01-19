"""
FastAPI application entry point for Simple Issue Tracker.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from app.core.config import settings
from app.api.endpoints import auth, health, managers, email_inboxes
# from app.api.endpoints import boards, tickets, public

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(managers.router, prefix="/api", tags=["Managers"])
app.include_router(email_inboxes.router, prefix="/api/inboxes", tags=["Email Inboxes"])
# app.include_router(boards.router, prefix="/api/boards", tags=["Boards"])
# app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
# app.include_router(public.router, prefix="/api/public", tags=["Public"])

# Serve frontend static files (production only)
# app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down application")
