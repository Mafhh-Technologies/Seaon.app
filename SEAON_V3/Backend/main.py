"""
Main FastAPI application entry point.
Sets up middleware, routers, exception handlers, and lifecycle events.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI #fastapi for creating the API application and defining routes, dependencies, and middleware.
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import production
from app.api.routes import auth, orders, inventory, bom
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    setup_logging()
    init_db()
    yield

app = FastAPI(
    title="SEAON Manufacturing Dashboard API",
    description="Backend API for inventory, production, orders, and BOM management.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── Middleware ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# ── Exception handlers ──────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(auth.router,
                   prefix="/api/auth",
                   tags=["Authentication"]
                   )
app.include_router(orders.router,
                   prefix="/api/orders",
                   tags=["Orders"]
                   )
app.include_router(inventory.router,
                   prefix="/api/inventory",
                   tags=["Inventory"]
                   )
app.include_router(bom.router,
                   prefix="/api/bom",
                   tags=["Bill of Materials"]
                   )
app.include_router(production.router,
                   prefix="/api/production",
                   tags=["Production"]
                   )

@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint for Docker / load balancers."""
    return {"status": "healthy", "version": app.version}