from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class BusinessBase(BaseModel):
    name: str
    registration_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = "Trinidad and Tobago"
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    registration_date: Optional[datetime] = None
    status: Optional[str] = None
    annual_revenue_range: Optional[str] = None
    employee_count_range: Optional[str] = None
    directors: Optional[List[Dict[str, Any]]] = None
    shareholders: Optional[List[Dict[str, Any]]] = None
    sic_codes: Optional[List[str]] = None
    naics_codes: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: bool = False
    verification_score: int = 0

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    is_verified: Optional[bool] = None
    verification_score: Optional[int] = None

class BusinessResponse(BusinessBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BusinessSearch(BaseModel):
    query: str
    city: Optional[str] = None
    industry: Optional[str] = None
    business_type: Optional[str] = None
    status: Optional[str] = None
    skip: int = 0
    limit: int = 100

class BusinessStats(BaseModel):
    total_businesses: int
    by_status: Dict[str, int]
    by_city: Dict[str, int]
    by_industry: Dict[str, int]
    last_updated: Optional[datetime] = None

class PaginatedResponse(BaseModel):
    data: List[BusinessResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    @classmethod
    def from_query(cls, data: List[BusinessResponse], total: int, skip: int, limit: int):
        return cls(
            data=data,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(data)) < total
        )