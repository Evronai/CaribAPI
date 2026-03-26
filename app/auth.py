from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets

from app.config import settings
from app.database import get_db
from app.models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

async def get_current_user(
    api_key: str = Depends(api_key_header),
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from API key or Bearer token
    Priority: API Key > Bearer Token
    """
    user = None
    
    # Try API key first
    if api_key:
        user = db.query(User).filter(User.api_key == api_key).first()
    
    # Try Bearer token if no API key found
    elif token:
        try:
            payload = jwt.decode(
                token.credentials, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user = db.query(User).filter(User.email == email).first()
    
    # No authentication provided
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user

def check_rate_limit(user: User, db: Session) -> bool:
    """
    Check if user has exceeded their rate limits
    Returns True if allowed, False if rate limited
    """
    from datetime import date
    
    today = date.today()
    
    # Reset daily counter if new day
    if user.last_request_at and user.last_request_at.date() != today:
        user.requests_used_today = 0
    
    # Check daily limit
    if user.requests_used_today >= user.daily_limit:
        return False
    
    # Check monthly limit (simplified - resets on 1st of month)
    if user.requests_used_month >= user.monthly_limit:
        return False
    
    return True

def increment_request_count(user: User, db: Session):
    """Increment user's request counters"""
    from datetime import date
    
    today = date.today()
    
    # Reset daily counter if new day
    if user.last_request_at and user.last_request_at.date() != today:
        user.requests_used_today = 0
    
    # Increment counters
    user.requests_used_today += 1
    user.requests_used_month += 1
    user.last_request_at = datetime.utcnow()
    
    db.commit()