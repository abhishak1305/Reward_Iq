"""
FastAPI application entry point.
Handles lifespan (DB init), CORS, and route inclusion.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys

from backend.core.config import settings
from backend.core.database import create_all_tables
from backend.api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ensure all tables exist and database is seeded on every startup.
    Uses CREATE TABLE IF NOT EXISTS and idempotency checks in seed().
    """
    try:
        await create_all_tables()
        sys.stdout.write("[INFO] Database tables verified/created.\n")
        
        # Auto-seed if needed
        from backend.seed import seed
        await seed()
        sys.stdout.write("[INFO] Database seeding check complete.\n")
        sys.stdout.flush()
    except Exception as e:
        sys.stdout.write(f"[WARNING] Startup issue: {type(e).__name__}: {e}\n")
        sys.stdout.flush()
    yield


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/api/health", tags=["health"])
async def health():
    return JSONResponse({"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION})
