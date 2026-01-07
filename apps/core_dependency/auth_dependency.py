import uuid

from fastapi import Request, Depends, HTTPException, Header, Cookie, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.settings import settings
from apps.core_dependency.redis_dependency import RedisDependency
from apps.core_dependency.db_dependency import DBDependency
from apps.database.models.user import User
from apps.auth.utils import decode_access_token, create_access_token


async def get_current_user(
    request: Request,
    authorization: str | None = Header(None),
    refresh_token: str | None = Cookie(None, alias="refresh_token"),
    redis: Redis = Depends(RedisDependency().client),
    db: AsyncSession = Depends(DBDependency().get_session),
):
    try:
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            try:
                user_id = decode_access_token(token)
                user = await db.get(User, user_id)
                if user:
                    request.state.user = user
                    return user

            except:
                pass

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No credentials."
            )

        user_id_str = await redis.get(f"refresh:{refresh_token}")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired."
            )

        user = await db.get(User, uuid.UUID(user_id_str))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
            )

        await redis.expire(
            f"refresh:{refresh_token}", settings.refresh_token_expire_days * 86400
        )

        request.state.new_access_token = create_access_token(str(user.id))
        request.state.user = user

        return user

    finally:
        await redis.aclose()
        await db.aclose()
