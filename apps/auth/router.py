from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.params import Cookie
from starlette import status
import uuid

from apps.core_dependency.redis_dependency import RedisDependency
from apps.core.settings import settings
from apps.auth.schemas import CreateUser, RegisterUser, LoginUser
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


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        user_data: RegisterUser,
        response: Response,
):
    hashed_password = hash_password(user_data.password)
    user = CreateUser(**user_data.__dict__, hashed_password=hashed_password)

    try:
        user = await auth_manager.register(user)
        await _create_session(user.id, response)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login")
async def login(
        credentials: LoginUser,
        response: Response,
):

    try:
        user = await auth_manager.authenticate_user(credentials)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные логин или пароль.")

    await _create_session(user.id, response)



@router.post("/logout")
async def logout(
        refresh_token: str | None = Cookie(None, alias="refresh_token"),
        redis = Depends(RedisDependency().client)
):
    if refresh_token:
        await redis.delete(f"refresh:{refresh_token}")

    response = Response(content='{"msg":"logged out"}', media_type="application/json")
    response.delete_cookie("refresh_token", path="/")
    return response