import resend
from redis.asyncio import Redis
from apps.core.settings import settings
from apps.auth.utils import create_verification_code

resend.api_key = settings.resend_api_key

class EmailService:
    """Отправка email писем"""

    @staticmethod
    async def send_register_verification_email(email: str, code: str):
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [email],
            "subject": "Код подтверждения регистрации",
            "html": f"<html>{code}</html>",
        })

class VerificationCodeService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create_register_verification_code(self, email: str) -> str:
        code = create_verification_code()
        await self.redis.setex(f"register:verify:{email}", 7200, code)

        return code

    async def verify_register_code(self, email: str, code: str) -> bool:
        valid_code = await self.redis.get(f"register:verify:{email}")
        if valid_code and valid_code == code:
            return True

        return False

    async def delete_register_verification_code(self, email: str):
        await self.redis.delete(f"register:verify:{email}")