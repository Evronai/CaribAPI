from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Business(BaseModel):
    __tablename__ = "businesses"
    
    # Basic info
    name = Column(String, index=True, nullable=False)
    registration_number = Column(String, unique=True, index=True)
    
    # Contact
    address = Column(Text)
    city = Column(String)
    region = Column(String)  # e.g., "San Fernando", "Port of Spain"
    country = Column(String, default="Trinidad and Tobago")
    postal_code = Column(String)
    
    # Contact details
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    
    # Business details
    business_type = Column(String)  # e.g., "Limited Liability", "Sole Proprietor"
    industry = Column(String)  # e.g., "Retail", "Manufacturing", "Services"
    sub_industry = Column(String)
    
    # Registration
    registration_date = Column(DateTime(timezone=True))
    status = Column(String)  # "Active", "Inactive", "Dissolved"
    
    # Financial (if available)
    annual_revenue_range = Column(String)  # e.g., "$100k-$500k"
    employee_count_range = Column(String)  # e.g., "10-50"
    
    # Directors/Owners (stored as JSON for simplicity)
    directors = Column(JSON)  # List of director names
    shareholders = Column(JSON)  # List of shareholder info
    
    # Additional data
    sic_codes = Column(JSON)  # Standard Industrial Classification (stored as JSON list)
    naics_codes = Column(JSON)  # North American Industry Classification (stored as JSON list)
    
    # Location data
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Source tracking
    source = Column(String)  # Where we got this data
    source_url = Column(String)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_score = Column(Integer, default=0)  # 0-100 confidence score
    
    # Search optimization
    search_vector = Column(Text)  # For full-text search
    
    def __repr__(self):
        return f"<Business {self.name} ({self.registration_number})>"