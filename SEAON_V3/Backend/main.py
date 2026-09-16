"""Application entry point for the SEAON backend."""

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.bom import router as bom_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.orders import router as orders_router
from app.core.database import init_db

app = FastAPI(
	title="SEAON API",
	description="Backend API for SEAON.",
	version="1.0.0",
)

# Keep the API usable from local development frontends while allowing the
# deployment environment to provide stricter CORS rules later.
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(bom_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(orders_router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
	init_db()


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
	"""Return basic API metadata."""
	return {"name": "SEAON API", "status": "ok"}


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, Any]:
	"""Provide a lightweight health check for monitoring and deployments."""
	return {
		"status": "healthy",
		"timestamp": datetime.now(timezone.utc).isoformat(),
	}


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
