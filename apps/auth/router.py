from fastapi import APIRouter, HTTPException, Response, Depends
from starlette import status
import uuid

from apps.core_dependency.redis_dependency import RedisDependency
from apps.core.settings import settings
from apps.auth.schemas import CreateUser, RegisterUser
from .utils import hash_password, create_refresh_token
from . import auth_manager

router = APIRouter(prefix="/auth", tags=["auth"])

async def _create_session(user_id: uuid, response: Response):
    redis = await RedisDependency().client()

    refresh_token = create_refresh_token()
    await redis.setex(f"refresh:{refresh_token}", settings.refresh_token_expire_days * 86400, str(user_id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/"
    )

    await redis.close()


@router.post("/register/send-verify-code")
async def send_verify_code(email: str):
    await auth_manager.send_register_code(email)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        code: str,
        user_data: RegisterUser,
        response: Response,
):
    hashed_password = hash_password(user_data.password)
    user = CreateUser(**user_data.__dict__, hashed_password=hashed_password)

    try:
        user = await auth_manager.register(user, code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    await _create_session(user.id, response)