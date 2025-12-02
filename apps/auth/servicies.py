import resend
import secrets
from datetime import datetime, timedelta, timezone
from redis.asyncio import Redis
from apps.core.settings import settings

resend.api_key = settings.resend_api_key

class EmailService:
    """Отправка email писем"""

    @staticmethod
    async def send_verification_email(email: str, token: str):
        link = f"{settings.frontend_url}/auth/verify-email/{token}"

        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [email],
            "subject": "Подтвердите регистрацию в Barter",
            "html": f"<html>{link}</html>",
        })

class VerificationTokenService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create_verification_token(self, email: str) -> str:
        token = secrets.token_urlsafe(48)
        expires_at = int((datetime.now(tz=timezone.utc).replace(tzinfo=None) + timedelta(hours=24)).timestamp())
        full_token = f"{token}.{expires_at}"

        await self.redis.setex(f"verify:token:{full_token}", 86_400, email.lower())
        await self.redis.setex(f"verify:email:{email.lower()}", 86_400, full_token)

        return full_token


    async def verify_token(self, token: str) -> str | None:
        email = await self.redis.get(f"verify:token:{token}")
        if not email:
            return None

        try:
            _, exp = token.split(".", 1)
            if int(exp) < datetime.now(tz=timezone.utc).replace(tzinfo=None).timestamp():
                await self.redis.delete(f"verify:token:{token}", f"verify:email:{email.lower()}")

                return None

        except:
            return None

        return email.lower()


    async def delete_verification_token(self, token: str):
        email = await self.redis.get(f"verify:token:{token}")
        await self.redis.delete(f"verify:token:{token}", f"verify:email:{email}")