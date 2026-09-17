"""
SQLAlchemy engine, session factory, and base model.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# SQLite needs a special flag for multi-threaded FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: yields a database session and guarantees close.
    Usage: def endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables and seed default admin user (called on startup)."""
    # Import models so SQLAlchemy knows about them before create_all
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Seed default admin user
    from app.services.auth_service import AuthService
    AuthService.seed_default_admin()