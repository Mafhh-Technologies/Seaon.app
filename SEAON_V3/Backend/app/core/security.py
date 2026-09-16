import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
	salt = secrets.token_hex(16)
	digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
	return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
	try:
		algorithm, rounds, salt, expected = encoded.split("$", 3)
		if algorithm != "pbkdf2_sha256":
			return False
		actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
		return hmac.compare_digest(actual, expected)
	except (ValueError, TypeError):
		return False


def create_access_token() -> str:
	return secrets.token_urlsafe(32)
