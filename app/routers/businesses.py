from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
import logging

from app.database import get_db
from app.auth import get_current_user, increment_request_count
from app.models.user import User
from app.models.business import Business
from app.models.api_request import APIRequest
from app.schemas.business import BusinessResponse, BusinessSearch

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[BusinessResponse])
async def get_businesses(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    city: Optional[str] = None,
    industry: Optional[str] = None,
    business_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get businesses with filtering and pagination
    """
    # Start timing for response time
    import time
    start_time = time.time()
    
    try:
        # Build query
        query = db.query(Business)
        
        # Apply filters
        if city:
            query = query.filter(Business.city.ilike(f"%{city}%"))
        if industry:
            query = query.filter(Business.industry.ilike(f"%{industry}%"))
        if business_type:
            query = query.filter(Business.business_type.ilike(f"%{business_type}%"))
        if status:
            query = query.filter(Business.status == status)
        
        # Apply pagination
        total_count = query.count()
        businesses = query.offset(skip).limit(limit).all()
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API request
        log_api_request(
            db=db,
            user=current_user,
            endpoint=request.url.path,
            method=request.method,
            query_params=str(request.query_params),
            status_code=200,
            response_time_ms=response_time_ms,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Increment user's request count
        increment_request_count(current_user, db)
        
        return businesses
        
    except Exception as e:
        logger.error(f"Error fetching businesses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search", response_model=List[BusinessResponse])
async def search_businesses(
    request: Request,
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search businesses by name, registration number, or other fields
    """
    import time
    start_time = time.time()
    
    try:
        # Build search query
        query = db.query(Business).filter(
            or_(
                Business.name.ilike(f"%{q}%"),
                Business.registration_number.ilike(f"%{q}%"),
                Business.address.ilike(f"%{q}%"),
                Business.city.ilike(f"%{q}%"),
                Business.industry.ilike(f"%{q}%")
            )
        )
        
        total_count = query.count()
        businesses = query.offset(skip).limit(limit).all()
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API request
        log_api_request(
            db=db,
            user=current_user,
            endpoint=request.url.path,
            method=request.method,
            query_params=str(request.query_params),
            status_code=200,
            response_time_ms=response_time_ms,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        increment_request_count(current_user, db)
        
        return businesses
        
    except Exception as e:
        logger.error(f"Error searching businesses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business_by_id(
    request: Request,
    business_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get business by ID
    """
    import time
    start_time = time.time()
    
    try:
        business = db.query(Business).filter(Business.id == business_id).first()
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API request
        log_api_request(
            db=db,
            user=current_user,
            endpoint=request.url.path,
            method=request.method,
            query_params=str(request.query_params),
            status_code=200,
            response_time_ms=response_time_ms,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        increment_request_count(current_user, db)
        
        return business
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/registration/{registration_number}", response_model=BusinessResponse)
async def get_business_by_registration(
    request: Request,
    registration_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get business by registration number
    """
    import time
    start_time = time.time()
    
    try:
        business = db.query(Business).filter(
            Business.registration_number == registration_number
        ).first()
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API request
        log_api_request(
            db=db,
            user=current_user,
            endpoint=request.url.path,
            method=request.method,
            query_params=str(request.query_params),
            status_code=200,
            response_time_ms=response_time_ms,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        increment_request_count(current_user, db)
        
        return business
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching business by registration {registration_number}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/city/{city_name}", response_model=List[BusinessResponse])
async def get_businesses_by_city(
    request: Request,
    city_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get businesses by city
    """
    import time
    start_time = time.time()
    
    try:
        businesses = db.query(Business).filter(
            Business.city.ilike(f"%{city_name}%")
        ).offset(skip).limit(limit).all()
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API request
        log_api_request(
            db=db,
            user=current_user,
            endpoint=request.url.path,
            method=request.method,
            query_params=str(request.query_params),
            status_code=200,
            response_time_ms=response_time_ms,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        increment_request_count(current_user, db)
        
        return businesses
        
    except Exception as e:
        logger.error(f"Error fetching businesses in city {city_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/industry/{industry_name}", response_model=List[BusinessResponse])
async def get_businesses_by_industry(
    request: Request,
    industry_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get businesses by industry
    """
    import time
    start_time = time.time()
    
    try:
        businesses = db.query(Business).filter(
            Business.industry.ilike(f"%{industry_name}%")
        ).offset(skip).limit(limit).all()
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API request
        log_api_request(
            db=db,
            user=current_user,
            endpoint=request.url.path,
            method=request.method,
            query_params=str(request.query_params),
            status_code=200,
            response_time_ms=response_time_ms,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        increment_request_count(current_user, db)
        
        return businesses
        
    except Exception as e:
        logger.error(f"Error fetching businesses in industry {industry_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/summary")
async def get_business_stats(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get business statistics summary
    """
    import time
    start_time = time.time()
    
    try:
        # Get counts
        total_businesses = db.query(Business).count()
        
        # Count by status
        status_counts = db.query(
            Business.status, 
            db.func.count(Business.id)
        ).group_by(Business.status).all()
        
        # Count by city (top 10)
        city_counts = db.query(
            Business.city,
            db.func.count(Business.id)
        ).filter(Business.city.isnot(None)).group_by(Business.city).order_by(
            db.func.count(Business.id).desc()
        ).limit(10).all()
        
        # Count by industry (top 10)
        industry_counts = db.query(
            Business.industry,
            db.func.count(Business.id)
        ).filter(Business.industry.isnot(None)).group_by(Business.industry).order_by(
            db.func.count(Business.id).desc()
        ).limit(10).all()
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API request
        log_api_request(
            db=db,
            user=current_user,
            endpoint=request.url.path,
            method=request.method,
            query_params=str(request.query_params),
            status_code=200,
            response_time_ms=response_time_ms,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        increment_request_count(current_user, db)
        
        return {
            "total_businesses": total_businesses,
            "by_status": {status: count for status, count in status_counts},
            "by_city": {city: count for city, count in city_counts},
            "by_industry": {industry: count for industry, count in industry_counts},
            "last_updated": db.query(db.func.max(Business.last_updated)).scalar()
        }
        
    except Exception as e:
        logger.error(f"Error fetching business stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def log_api_request(
    db: Session,
    user: User,
    endpoint: str,
    method: str,
    query_params: str,
    status_code: int,
    response_time_ms: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Log an API request to the database
    """
    try:
        api_request = APIRequest(
            user_id=user.id,
            endpoint=endpoint,
            method=method,
            query_params=query_params,
            status_code=status_code,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            cost_units=1  # Each request costs 1 unit
        )
        
        db.add(api_request)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to log API request: {str(e)}")
        # Don't raise, just log the error