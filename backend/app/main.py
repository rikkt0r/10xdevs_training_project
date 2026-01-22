"""
FastAPI application entry point for Simple Issue Tracker.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from app.core.config import settings
from app.core.middleware import limiter, SecurityHeadersMiddleware
from app.api.endpoints import auth, health, managers, email_inboxes, boards, tickets, standby_queue, dashboard, public

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

# Create APScheduler instance
scheduler = AsyncIOScheduler(timezone="UTC")

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(managers.router, prefix="/api", tags=["Managers"])
app.include_router(email_inboxes.router, prefix="/api/inboxes", tags=["Email Inboxes"])
app.include_router(boards.router, prefix="/api/boards", tags=["Boards"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(standby_queue.router, prefix="/api/standby-queue", tags=["Standby Queue"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(public.router, prefix="/api/public", tags=["Public"])

# Serve frontend static files (production only)
# app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")

    # Start APScheduler
    scheduler.start()
    logger.info("APScheduler started")

    # Initialize email polling jobs
    from app.services.email_polling_service import initialize_polling_jobs
    await initialize_polling_jobs(scheduler)
    logger.info("Email polling jobs initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down application")

    # Shutdown APScheduler gracefully
    scheduler.shutdown(wait=True)
    logger.info("APScheduler shut down")
