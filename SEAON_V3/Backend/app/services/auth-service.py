from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemes.user import UserCreate


def register_user(db: Session, payload: UserCreate) -> User:
	if db.scalar(select(User).where(User.email == str(payload.email).lower())):
		raise ConflictError("Email is already registered")
	user = User(
		name=payload.name.strip(),
		email=str(payload.email).lower(),
		password_hash=hash_password(payload.password),
		role=payload.role,
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


def authenticate_user(db: Session, email: str, password: str) -> User:
	user = db.scalar(select(User).where(User.email == email.lower()))
	if user is None or not user.is_active or not verify_password(password, user.password_hash):
		raise NotFoundError("Invalid email or password")
	return user


def main() -> None:
	print("Authentication service helpers are ready.")


if __name__ == "__main__":
	main()
