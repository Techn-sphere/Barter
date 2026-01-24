from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError

from apps.auth.schemas import CreateUser, LoginUser
from apps.core_dependency.db_dependency import DBDependency
from apps.core_dependency.redis_dependency import RedisDependency
from apps.database.models import User
from apps.auth.crud import create_user, get_user_by_email
from apps.auth.utils import hash_password, verify_password


class AuthManager:
    def __init__(self, redis: Redis = RedisDependency(), db: DBDependency = DBDependency()) -> None:
        self.model = User
        self.db = db
        self.redis = redis


    async def register(self, user: CreateUser) -> User:
        db_session = await self.db.get_session()
        async with db_session as session:
            try:
                user_data = await create_user(session, user)
                return user_data
            except IntegrityError:
                raise ValueError("Пользователь уже существует")


    async def authenticate_user(self, credentials: LoginUser) -> User | None:
        db_session = await self.db.get_session()
        async with db_session as session:
            user = await get_user_by_email(session, credentials.email.__str__())
            if not user:
                return None

            if not verify_password(credentials.password, user.hashed_password):
                return None

            return user