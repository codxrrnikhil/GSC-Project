from datetime import datetime

from fastapi import APIRouter

from app.schemas.user import UserCreate
from app.services.mongodb import db

router = APIRouter()


@router.post("/users")
async def create_user(user: UserCreate):
    user_dict = user.model_dump()
    user_dict["is_active"] = True
    user_dict["created_at"] = datetime.utcnow()

    result = await db.users.insert_one(user_dict)

    created = await db.users.find_one({"_id": result.inserted_id})
    created["id"] = str(created["_id"])
    del created["_id"]
    return created


@router.get("/users")
async def get_users():
    users = []
    async for user in db.users.find():
        user["id"] = str(user["_id"])
        user["created_at"] = user["created_at"].isoformat()  # ✅ FIX
        del user["_id"]
        users.append(user)
    return users