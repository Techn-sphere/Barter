import uuid
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
import jwt
import secrets
from apps.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(user_id: str) -> str:
    expires = datetime.now(tz=timezone.utc).replace(tzinfo=None) + timedelta(seconds=20)
    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": expires,
            "iat": datetime.now(tz=timezone.utc).replace(tzinfo=None),
        },
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm)

def decode_access_token(token: str) -> uuid:
    payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
    user_id: str = payload.get("sub")
    if not user_id:
        raise InvalidSignatureError
    return uuid.UUID(user_id)

def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)