from sqlalchemy import insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.schemas import CreateUser
from apps.database.models import User


async def create_user(session: AsyncSession, user: CreateUser) -> User:
    query = insert(User).values(**user.__dict__).returning(User)

    result = await session.execute(query)
    await session.commit()
    return result.scalar_one()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await session.execute(query)

    return result.scalar_one_or_none()
