from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import stripe
from typing import Optional

from app.config import settings
from app.database import get_db
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    generate_api_key,
    get_current_user
)
from app.models.user import User, UserPlan
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token
from app.services.stripe_service import create_stripe_customer

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate API key
    api_key = generate_api_key()
    
    # Create Stripe customer
    stripe_customer = None
    if user_data.stripe_payment_method_id:
        try:
            stripe_customer = create_stripe_customer(
                email=user_data.email,
                name=user_data.full_name,
                payment_method_id=user_data.stripe_payment_method_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment method error: {str(e)}"
            )
    
    # Create user
    hashed_password = get_password_hash(user_data.password) if user_data.password else None
    
    # Set limits based on plan
    daily_limit = settings.rate_limit_free
    monthly_limit = settings.rate_limit_free * 30
    
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        company=user_data.company,
        hashed_password=hashed_password,
        api_key=api_key,
        plan=UserPlan.FREE,
        stripe_customer_id=stripe_customer.id if stripe_customer else None,
        daily_limit=daily_limit,
        monthly_limit=monthly_limit,
        is_verified=False,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password, get access token
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    """
    return current_user

@router.post("/api-key/reset")
async def reset_api_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset API key (invalidates old one)
    """
    new_api_key = generate_api_key()
    current_user.api_key = new_api_key
    db.commit()
    
    return {
        "message": "API key reset successfully",
        "new_api_key": new_api_key
    }

@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current usage statistics
    """
    from datetime import date
    
    today = date.today()
    
    # Calculate remaining requests
    daily_remaining = max(0, current_user.daily_limit - current_user.requests_used_today)
    monthly_remaining = max(0, current_user.monthly_limit - current_user.requests_used_month)
    
    return {
        "plan": current_user.plan.value,
        "limits": {
            "daily": current_user.daily_limit,
            "monthly": current_user.monthly_limit
        },
        "usage": {
            "today": current_user.requests_used_today,
            "this_month": current_user.requests_used_month,
            "last_request": current_user.last_request_at
        },
        "remaining": {
            "daily": daily_remaining,
            "monthly": monthly_remaining
        }
    }

@router.post("/upgrade")
async def upgrade_plan(
    plan: UserPlan,
    payment_method_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user plan
    """
    from app.services.stripe_service import create_subscription
    
    if current_user.plan == plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are already on the {plan.value} plan"
        )
    
    # Get Stripe price ID for the plan
    if plan == UserPlan.PRO:
        price_id = settings.stripe_price_pro
    elif plan == UserPlan.BUSINESS:
        price_id = settings.stripe_price_business
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    try:
        # Create or update subscription
        subscription = create_subscription(
            customer_id=current_user.stripe_customer_id,
            price_id=price_id,
            payment_method_id=payment_method_id
        )
        
        # Update user plan and limits
        current_user.plan = plan
        current_user.stripe_subscription_id = subscription.id
        
        # Update limits based on plan
        if plan == UserPlan.PRO:
            current_user.daily_limit = settings.rate_limit_pro
            current_user.monthly_limit = settings.rate_limit_pro * 30
        elif plan == UserPlan.BUSINESS:
            current_user.daily_limit = settings.rate_limit_business
            current_user.monthly_limit = settings.rate_limit_business * 30
        
        db.commit()
        
        return {
            "message": f"Successfully upgraded to {plan.value} plan",
            "plan": plan.value,
            "new_limits": {
                "daily": current_user.daily_limit,
                "monthly": current_user.monthly_limit
            },
            "subscription_id": subscription.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upgrade failed: {str(e)}"
        )

@router.post("/downgrade")
async def downgrade_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Downgrade to free plan
    """
    from app.services.stripe_service import cancel_subscription
    
    if current_user.plan == UserPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on the free plan"
        )
    
    try:
        # Cancel subscription if exists
        if current_user.stripe_subscription_id:
            cancel_subscription(current_user.stripe_subscription_id)
        
        # Update user to free plan
        current_user.plan = UserPlan.FREE
        current_user.stripe_subscription_id = None
        current_user.daily_limit = settings.rate_limit_free
        current_user.monthly_limit = settings.rate_limit_free * 30
        
        db.commit()
        
        return {
            "message": "Successfully downgraded to free plan",
            "plan": "free",
            "new_limits": {
                "daily": current_user.daily_limit,
                "monthly": current_user.monthly_limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Downgrade failed: {str(e)}"
        )