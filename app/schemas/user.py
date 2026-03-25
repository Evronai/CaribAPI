from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    company: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for API key only users
    stripe_payment_method_id: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    api_key: str
    plan: UserPlan
    is_active: bool
    is_verified: bool
    requests_used_today: int
    requests_used_month: int
    daily_limit: int
    monthly_limit: int
    last_request_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None

class UsageStats(BaseModel):
    plan: UserPlan
    limits: dict
    usage: dict
    remaining: dict