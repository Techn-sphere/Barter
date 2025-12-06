import logging

from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from apps.auth.schemas import CreateUser, UserReturnData
from apps.core_dependency.db_dependency import DBDependency
from apps.core_dependency.redis_dependency import RedisDependency
from apps.database.models import User
from apps.auth.servicies import VerificationTokenService, EmailService


class UserManager:
    def __init__(self, redis: Redis = RedisDependency(), db: DBDependency = DBDependency()) -> None:
        self.model = User
        self.db = db
        self.redis = redis
        self.token_service = None

    async def create_token_service(self):
        if self.token_service is None:
            redis = await self.redis.client()
            self.token_service = VerificationTokenService(redis)

    async def create_user(self, user: CreateUser) -> UserReturnData:
        await self.create_token_service()

        db_session = await self.db.get_session()
        async with db_session as session:
            query = insert(self.model).values(**user.model_dump()).returning(self.model)

            try:
                result = await session.execute(query)
            except IntegrityError:
                raise ValueError("Пользователь уже существует")

            await session.commit()

            user_data = result.scalar_one()

            token = await self.token_service.create_verification_token(user_data.email.lower())
            logging.info(token)
            await EmailService.send_verification_email(user_data.email.lower(), token)

            return UserReturnData(**user_data.__dict__)


    async def verify_email(self, token: str):
        await self.create_token_service()

        db_session = await self.db.get_session()
        async with db_session as session:
            email = await self.token_service.verify_token(token)
            if not email:
                raise ValueError("Ссылка недействительна или просрочена")

            query = select(User).where(User.email == email)
            result = await session.execute(query)

            user: User = result.scalar_one_or_none()
            if not user:
                raise ValueError("Пользователь не найден")

            if user.is_email_verified:
                return user

            user.is_email_verified = True
            session.add(user)

            await session.commit()

            await self.token_service.delete_verification_token(token)
            return user
