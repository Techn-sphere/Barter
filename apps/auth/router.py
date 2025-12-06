from fastapi import APIRouter, HTTPException
from apps.auth.schemas import CreateUser, UserReturnData, RegisterUser
from . import user_manager
from .utils import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserReturnData)
async def register(user_data: RegisterUser):
    hashed_password = hash_password(user_data.password)
    user = CreateUser(**user_data.__dict__, hashed_password=hashed_password)

    try:
        user = await user_manager.create_user(user)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/verify-email/{token}")
async def verify_email(token: str):
    try:
        await user_manager.verify_email(token)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"msg": "Email успешно подтвержден"}