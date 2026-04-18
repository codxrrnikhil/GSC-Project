from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
