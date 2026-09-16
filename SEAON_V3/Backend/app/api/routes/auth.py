from datetime import datetime, timezone
from secrets import token_urlsafe

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(min_length=6)


class User(BaseModel):
	id: int
	name: str
	email: EmailStr
	role: str = "admin"


class LoginResponse(BaseModel):
	token: str
	user: User


_users = {
	"admin@seaon.com": User(
		id=1,
		name="Administrator",
		email="admin@seaon.com",
	)
}
_tokens: dict[str, User] = {}


def _current_user(authorization: str | None) -> User:
	if not authorization or not authorization.startswith("Bearer "):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
	user = _tokens.get(authorization.removeprefix("Bearer ").strip())
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
	return user


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
	user = _users.get(str(payload.email).lower())
	if user is None:
		user = User(id=len(_users) + 1, name=str(payload.email).split("@")[0].title(), email=payload.email)
		_users[str(payload.email).lower()] = user
	token = token_urlsafe(32)
	_tokens[token] = user
	return LoginResponse(token=token, user=user)


@router.get("/me", response_model=User)
async def me(authorization: str | None = Header(default=None)) -> User:
	return _current_user(authorization)


@router.post("/logout")
async def logout(authorization: str | None = Header(default=None)) -> dict[str, str]:
	if authorization and authorization.startswith("Bearer "):
		_tokens.pop(authorization.removeprefix("Bearer ").strip(), None)
	return {"message": "Logged out successfully", "timestamp": datetime.now(timezone.utc).isoformat()}
