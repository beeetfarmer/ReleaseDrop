"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from .database import init_db
from .routes import artists_router, releases_router
from .routes.integrations import router as integrations_router
from .scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize database and start scheduler
    print("Starting ReleaseDrop...")
    init_db()
    print("Database initialized")
    start_scheduler()
    print("Scheduler started")

    yield

    # Shutdown: Stop scheduler
    print("Stopping scheduler...")
    stop_scheduler()
    print("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="ReleaseDrop",
    description="Track your favorite Spotify artists and get notified of new releases",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
# Get allowed origins from environment variable or use safe defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(artists_router)
app.include_router(releases_router)
app.include_router(integrations_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "ReleaseDrop API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "releasedrop"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8619, reload=True)
