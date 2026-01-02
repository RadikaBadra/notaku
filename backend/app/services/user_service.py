from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from bson import ObjectId

from app.core.database import get_database
from app.core.security.password import PasswordHasher
from app.core.security.jwt import create_access_token, verify_token
from app.core.email import send_verification_email, send_password_reset_email
from app.models.user import UserCreate, Token, UserResponse, UserUpdate


class UserService:

    @staticmethod
    async def register_user(data: UserCreate):
        db = get_database()

        if await db.users.find_one({"email": data.email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        if await db.pending_users.find_one({"email": data.email}):
            raise HTTPException(status_code=400, detail="Verification email already sent")

        hashed_password = PasswordHasher.bcrypt(data.password[:72])

        pending_doc = {
            "username": data.username,
            "email": data.email,
            "password": hashed_password,
            "created_at": datetime.now(timezone.utc),
        }

        result = await db.pending_users.insert_one(pending_doc)

        token = create_access_token({"pending_id": str(result.inserted_id)})
        link = f"http://localhost:8000/api/v1/auth/verify?token={token}"

        send_verification_email(data.email, link)

        return {"message": "Verification email sent"}

    @staticmethod
    async def verify_email(token: str) -> Token:
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        pending_id = payload.get("pending_id")
        if not pending_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        db = get_database()

        pending_user = await db.pending_users.find_one(
            {"_id": ObjectId(pending_id)}
        )

        if not pending_user:
            raise HTTPException(status_code=400, detail="User not found")

        user_doc = {
            "username": pending_user["username"],
            "email": pending_user["email"],
            "password": pending_user["password"],
            "is_verified": True,
            "created_at": pending_user["created_at"],
            "updated_at": datetime.now(timezone.utc),
        }

        result = await db.users.insert_one(user_doc)
        await db.pending_users.delete_one({"_id": pending_user["_id"]})

        return create_access_token(
            {"user_id": str(result.inserted_id)}
        )

    @staticmethod
    async def login_user(identifier: str, password: str) -> Token:
        db = get_database()

        query = {"email": identifier} if "@" in identifier else {"username": identifier}
        user = await db.users.find_one(query)

        if not user or not PasswordHasher.verify(password, user["password"]):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not user.get("is_verified"):
            raise HTTPException(status_code=403, detail="Email not verified")


        return create_access_token(
            {"user_id": str(user["_id"])}
        )
        
    @staticmethod
    async def get_user_by_id(user_id: str):
        db = get_database()

        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})

        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(
            id=str(user_doc["_id"]),
            username=user_doc["username"],
            email=user_doc["email"],
            is_verified=user_doc["is_verified"],
            created_at=user_doc["created_at"],
        )
    
    @staticmethod
    async def update_user(user_id: str, data: UserUpdate) -> UserResponse:
        db = get_database()

        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})

        return UserResponse(
            id=str(user_doc["_id"]),
            username=user_doc["username"],
            email=user_doc["email"],
            is_verified=user_doc["is_verified"],
            created_at=user_doc["created_at"],
        )
    
    @staticmethod
    async def delete_user(user_id: str) -> None:
        db = get_database()

        result = await db.users.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    async def forgot_password(email: str):
        db = get_database()

        user = await db.users.find_one({"email": email})
        if not user:
            # ⚠️ Jangan bocorkan apakah email ada
            return {"message": "If the email exists, a reset link has been sent"}

        token = create_access_token(
            {"user_id": str(user["_id"]), "type": "reset"},
            expires_delta=timedelta(minutes=15)
        )

        link = f"http://localhost:3000/reset-password?token={token}"

        send_password_reset_email(email, link)

        return {"message": "If the email exists, a reset link has been sent"}


    @staticmethod
    async def reset_password(token: str, new_password: str) -> None:
        payload = verify_token(token)
        if not payload or payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        db = get_database()

        hashed_password = PasswordHasher.bcrypt(new_password[:72])

        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_password, "updated_at": datetime.now(timezone.utc)}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")