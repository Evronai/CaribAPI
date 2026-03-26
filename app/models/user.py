from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.models.base import BaseModel

class UserPlan(str, PyEnum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"

class User(BaseModel):
    __tablename__ = "users"
    
    # Basic info
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    company = Column(String)
    
    # Authentication
    hashed_password = Column(String)
    api_key = Column(String, unique=True, index=True, nullable=False)
    
    # Subscription
    plan = Column(Enum(UserPlan), default=UserPlan.FREE, nullable=False)
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    
    # Usage tracking
    requests_used_today = Column(Integer, default=0)
    requests_used_month = Column(Integer, default=0)
    last_request_at = Column(DateTime(timezone=True))
    
    # Limits
    daily_limit = Column(Integer, default=100)  # Will be set based on plan
    monthly_limit = Column(Integer, default=3000)  # Will be set based on plan
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))
    
    # Timestamps
    last_login_at = Column(DateTime(timezone=True))
    
    # Relationships
    api_requests = relationship("APIRequest", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email} ({self.plan})>"