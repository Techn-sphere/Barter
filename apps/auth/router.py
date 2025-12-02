from fastapi import APIRouter, HTTPException
from apps.auth.managers import UserManager
from apps.auth.schemas import CreateUser, UserReturnData
from . import user_manager

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register():
    pass


@router.get("/verify-email/{token}")
async def verify_email(token: str):
    try:
        await user_manager.verify_email(token)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"msg": "Email успешно подтвержден"}