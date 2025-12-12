from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError

from apps.auth.schemas import CreateUser, LoginUser
from apps.core_dependency.db_dependency import DBDependency
from apps.core_dependency.redis_dependency import RedisDependency
from apps.database.models import User
from apps.auth.servicies import VerificationCodeService, EmailService
from apps.auth.crud import create_user, get_user_by_email
from apps.auth.utils import hash_password, verify_password


class AuthManager:
    def __init__(self, redis: Redis = RedisDependency(), db: DBDependency = DBDependency()) -> None:
        self.model = User
        self.db = db
        self.redis = redis
        self.code_service = None

    async def create_code_service(self):
        if self.code_service is None:
            redis = await self.redis.client()
            self.code_service = VerificationCodeService(redis)

    async def send_register_code(self, email: str):
        await self.create_code_service()

        code = await self.code_service.create_register_verification_code(email)
        await EmailService.send_verification_email(email, code)


    async def register(self, user: CreateUser, code: str) -> User:
        await self.create_code_service()

        is_valid_code = await self.code_service.verify_register_code(user.email, code)
        if not is_valid_code:
            raise ValueError("Недействительный код подтверждения")

        db_session = await self.db.get_session()
        async with db_session as session:
            try:
                user_data = await create_user(session, user)
                return user_data
            except IntegrityError:
                raise ValueError("Пользователь уже существует")

            finally:
                await self.code_service.delete_register_verification_code(user.email)



    async def send_login_code(self, email: str):
        await self.create_code_service()

        code = await self.code_service.create_login_verification_code(email)
        await EmailService.send_verification_email(email, code)


    async def authenticate_user(self, credentials: LoginUser, code: str) -> User | None:
        await self.create_code_service()

        is_valid_code = await self.code_service.verify_login_code(credentials.email, code)
        if not is_valid_code:
            raise ValueError("Недействительный код подтверждения")

        db_session = await self.db.get_session()
        async with db_session as session:
            try:
                user = await get_user_by_email(session, credentials.email.__str__())
                if not user:
                    return None

                if not verify_password(credentials.password, user.hashed_password):
                    return None

                return user
            finally:
                await self.code_service.delete_login_verification_code(credentials.email)