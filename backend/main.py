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
# Clean origins to ensure no trailing slashes or whitespace
clean_origins = [o.strip().rstrip('/') for o in settings.ALLOWED_ORIGINS if o]
# Add both variants (with and without trailing slash) for safety
final_origins = []
for o in clean_origins:
    final_origins.append(o)
    final_origins.append(f"{o}/")

sys.stdout.write(f"[INFO] CORS allowed origins: {final_origins}\n")
sys.stdout.flush()

app.add_middleware(
    CORSMiddleware,
    allow_origins=final_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/api/health", tags=["health"])
async def health():
    return JSONResponse({"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION})
