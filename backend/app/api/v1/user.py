from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.services.user_service import UserService
from app.models.user import Token, UserCreate, UserUpdate
from app.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: UserCreate):
    return await UserService.register_user(user)

@router.get("/verify", response_model=Token)
async def verify_email(token: str):
    return await UserService.verify_email(token)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await UserService.login_user(
        identifier=form_data.username,
        password=form_data.password
    )

@router.get("/detail")
async def get_user_details(user_id: str = Depends(get_current_user_id)):
    return await UserService.get_user_by_id(user_id)

@router.put("/update")
async def update_user(
    user_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
):
    return await UserService.update_user(user_id, user_data)

@router.delete("/delete")
async def delete_user(user_id: str = Depends(get_current_user_id)):
    await UserService.delete_user(user_id)
    return {"message": "User deleted successfully"}

@router.post("/request-password-reset")
async def request_password_reset(email: str):
    return await UserService.request_password_reset(email)

@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    return await UserService.reset_password(token, new_password)