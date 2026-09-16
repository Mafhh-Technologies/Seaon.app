import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
	app_name: str = os.getenv("SEAON_APP_NAME", "SEAON API")
	database_url: str = os.getenv("SEAON_DATABASE_URL", "sqlite:///./seaon.db")
	secret_key: str = os.getenv("SEAON_SECRET_KEY", "change-this-secret-in-production")
	access_token_expire_minutes: int = int(os.getenv("SEAON_TOKEN_EXPIRE_MINUTES", "60"))
	debug: bool = os.getenv("SEAON_DEBUG", "false").lower() == "true"


settings = Settings()
