from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError

from apps.auth.schemas import CreateUser
from apps.core_dependency.db_dependency import DBDependency
from apps.core_dependency.redis_dependency import RedisDependency
from apps.database.models import User
from apps.auth.servicies import VerificationTokenService, EmailService
from apps.auth.crud import create_user, verify_user


class AuthManager:
    def __init__(self, redis: Redis = RedisDependency(), db: DBDependency = DBDependency()) -> None:
        self.model = User
        self.db = db
        self.redis = redis
        self.token_service = None

    async def create_token_service(self):
        if self.token_service is None:
            redis = await self.redis.client()
            self.token_service = VerificationTokenService(redis)

    async def register(self, user: CreateUser):
        await self.create_token_service()

        db_session = await self.db.get_session()
        async with db_session as session:
            try:
                user_data = await create_user(session, user)
            except IntegrityError:
                raise ValueError("Пользователь уже существует")

            token = await self.token_service.create_verification_token(user_data.email)
            await EmailService.send_verification_email(user_data.email, token)

            return user_data


    async def verify_email(self, token: str):
        await self.create_token_service()

        db_session = await self.db.get_session()
        async with db_session as session:
            email = await self.token_service.verify_token(token)
            if not email:
                raise ValueError("Ссылка недействительна или просрочена")

            user = await verify_user(session, email)
            if not user:
                raise ValueError("Пользователь не найден")

            await session.commit()

            await self.token_service.delete_verification_token(token)
