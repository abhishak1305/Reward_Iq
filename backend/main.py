"""
FastAPI application entry point.
Handles lifespan (DB init), CORS, and route inclusion.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.database import create_all_tables
from backend.api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup (dev mode). Use Alembic in production."""
    if settings.ENVIRONMENT != "production":
        try:
            await create_all_tables()
        except Exception as e:
            # Server starts even if DB is not yet configured
            import sys
            sys.stdout.write(f"[WARNING] DB startup skipped: {type(e).__name__}\n")
            sys.stdout.write("  -> Set DATABASE_URL in backend/.env to connect a database.\n")
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
