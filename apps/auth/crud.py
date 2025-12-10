from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.schemas import CreateUser
from apps.database.models import User

async def create_user(session: AsyncSession, user: CreateUser) -> User:
    query = insert(User).values(
        email=user.email.__str__().lower(),
        hashed_password=user.hashed_password,
    ).returning(User)

    result = await session.execute(query)
    await session.commit()
    return result.scalar_one()

async def verify_user(session: AsyncSession, email: str) -> User | None:
    query = update(User).where(User.email == email).values(is_email_verified=True).returning(User)
    result = await session.execute(query)
    await session.commit()
    return result.scalar_one_or_none()
