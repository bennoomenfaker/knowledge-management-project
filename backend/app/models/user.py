from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    institution: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    institution: Optional[str] = None
    role: Optional[str] = None


class UserProfile(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    role: str
    institution: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    email: str
    email_confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    session: dict
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str