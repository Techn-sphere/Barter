from fastapi import APIRouter, HTTPException

from starlette import status

from apps.auth.schemas import CreateUser, RegisterUser
from . import auth_manager
from .utils import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterUser):
    hashed_password = hash_password(user_data.password)
    user = CreateUser(**user_data.__dict__, hashed_password=hashed_password)

    try:
        await auth_manager.register(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/verify-email/{token}")
async def verify_email(token: str):
    try:
        await auth_manager.verify_email(token)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"msg": "Email успешно подтвержден"}