from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
	name: str = Field(min_length=1, max_length=120)
	email: EmailStr
	password: str = Field(min_length=6)
	role: str = "viewer"


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(min_length=6)


class UserRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	email: EmailStr
	role: str
	is_active: bool


class TokenResponse(BaseModel):
	token: str
	user: UserRead
