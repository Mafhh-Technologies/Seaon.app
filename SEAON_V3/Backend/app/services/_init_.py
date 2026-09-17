"""
Auth service — registration, login, JWT issuance, default admin seeding.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole


class AuthService:
    # ── Registration ───────────────────────────────────────────────────────
    @staticmethod
    def create_user(db: Session, name: str, email: str, password: str, role: str = "viewer") -> User:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("A user with this email already exists.")

        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole(role),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # ── Authentication ─────────────────────────────────────────────────────
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def issue_token(user: User) -> str:
        return create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})

    # ── Seeding ────────────────────────────────────────────────────────────
    @staticmethod
    def seed_default_admin() -> None:
        """Create the default admin user on first startup if none exists."""
        db: Session = SessionLocal()
        try:
            exists = db.query(User).filter(User.email == settings.DEFAULT_ADMIN_EMAIL).first()
            if not exists:
                admin = User(
                    name=settings.DEFAULT_ADMIN_NAME,
                    email=settings.DEFAULT_ADMIN_EMAIL,
                    hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                    role=UserRole.ADMIN,
                )
                db.add(admin)
                db.commit()
                print(f"✔ Seeded default admin: {settings.DEFAULT_ADMIN_EMAIL}")
        finally:
            db.close()