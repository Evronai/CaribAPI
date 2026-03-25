#!/usr/bin/env python3
"""
Create sample data for CaribAPI
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.user import User, UserPlan
from app.models.business import Business
from app.auth import generate_api_key, get_password_hash
import random
from datetime import datetime, timedelta

# Sample business data for Trinidad
SAMPLE_BUSINESSES = [
    {
        "name": "Caribbean Brewery Ltd",
        "registration_number": "TRN20240001",
        "address": "12 Coffee Street",
        "city": "San Fernando",
        "region": "San Fernando",
        "phone": "+1-868-652-1234",
        "email": "info@caribbrewery.com",
        "website": "https://caribbrewery.com",
        "business_type": "Limited Liability",
        "industry": "Manufacturing",
        "sub_industry": "Beverage Production",
        "status": "Active",
        "annual_revenue_range": "$5M-$10M",
        "employee_count_range": "100-250",
        "directors": [{"name": "John Smith", "position": "CEO"}],
        "latitude": 10.2866,
        "longitude": -61.4686
    },
    {
        "name": "Trinidad Tech Solutions",
        "registration_number": "TRN20240002",
        "address": "45 Independence Square",
        "city": "Port of Spain",
        "region": "Port of Spain",
        "phone": "+1-868-623-4567",
        "email": "sales@tts.com",
        "website": "https://tts.com",
        "business_type": "Limited Liability",
        "industry": "Technology",
        "sub_industry": "Software Development",
        "status": "Active",
        "annual_revenue_range": "$1M-$5M",
        "employee_count_range": "50-100",
        "directors": [{"name": "Maria Gonzalez", "position": "CTO"}],
        "latitude": 10.6549,
        "longitude": -61.5019
    },
    {
        "name": "Island Foods Supermarket",
        "registration_number": "TRN20240003",
        "address": "78 Main Road",
        "city": "Chaguanas",
        "region": "Chaguanas",
        "phone": "+1-868-672-8910",
        "email": "contact@islandfoods.com",
        "website": "https://islandfoods.com",
        "business_type": "Sole Proprietor",
        "industry": "Retail",
        "sub_industry": "Grocery",
        "status": "Active",
        "annual_revenue_range": "$500K-$1M",
        "employee_count_range": "25-50",
        "directors": [{"name": "Robert Chang", "position": "Owner"}],
        "latitude": 10.5167,
        "longitude": -61.4167
    },
    {
        "name": "Caribbean Construction Co.",
        "registration_number": "TRN20240004",
        "address": "23 Wrightson Road",
        "city": "Port of Spain",
        "region": "Port of Spain",
        "phone": "+1-868-625-1122",
        "email": "projects@caribconstruct.com",
        "website": "https://caribconstruct.com",
        "business_type": "Limited Liability",
        "industry": "Construction",
        "sub_industry": "Commercial Construction",
        "status": "Active",
        "annual_revenue_range": "$10M-$50M",
        "employee_count_range": "250-500",
        "directors": [{"name": "David Brown", "position": "Managing Director"}],
        "latitude": 10.6549,
        "longitude": -61.5019
    },
    {
        "name": "Tropical Tourism Agency",
        "registration_number": "TRN20240005",
        "address": "56 Ariapita Avenue",
        "city": "Port of Spain",
        "region": "Port of Spain",
        "phone": "+1-868-627-3344",
        "email": "bookings@tropicaltourism.com",
        "website": "https://tropicaltourism.com",
        "business_type": "Partnership",
        "industry": "Tourism",
        "sub_industry": "Travel Agency",
        "status": "Active",
        "annual_revenue_range": "$250K-$500K",
        "employee_count_range": "10-25",
        "directors": [{"name": "Sarah Johnson", "position": "Partner"}],
        "latitude": 10.6549,
        "longitude": -61.5019
    }
]

# Additional sample data for variety
CITIES = ["Port of Spain", "San Fernando", "Chaguanas", "Arima", "Point Fortin", "Tunapuna"]
INDUSTRIES = ["Retail", "Manufacturing", "Services", "Construction", "Technology", "Healthcare", "Education", "Tourism"]
BUSINESS_TYPES = ["Limited Liability", "Sole Proprietor", "Partnership", "Corporation"]

def create_sample_businesses(db: Session, count: int = 100):
    """Create sample business records"""
    print(f"Creating {count} sample businesses...")
    
    # Add the predefined sample businesses
    for business_data in SAMPLE_BUSINESSES:
        business = Business(**business_data)
        business.registration_date = datetime.now() - timedelta(days=random.randint(1, 365*5))
        business.last_updated = datetime.now()
        db.add(business)
    
    # Generate additional random businesses
    for i in range(count - len(SAMPLE_BUSINESSES)):
        city = random.choice(CITIES)
        industry = random.choice(INDUSTRIES)
        business_type = random.choice(BUSINESS_TYPES)
        
        business = Business(
            name=f"Sample Business {i+6}",
            registration_number=f"TRN{20240000 + i + 6}",
            address=f"{random.randint(1, 999)} Sample Street",
            city=city,
            region=city,
            country="Trinidad and Tobago",
            phone=f"+1-868-{random.randint(600, 699)}-{random.randint(1000, 9999)}",
            email=f"info@samplebusiness{i+6}.com",
            website=f"https://samplebusiness{i+6}.com",
            business_type=business_type,
            industry=industry,
            sub_industry=f"{industry} Services",
            registration_date=datetime.now() - timedelta(days=random.randint(1, 365*5)),
            status=random.choice(["Active", "Active", "Active", "Inactive"]),  # Mostly active
            annual_revenue_range=random.choice(["$100K-$250K", "$250K-$500K", "$500K-$1M", "$1M-$5M"]),
            employee_count_range=random.choice(["1-10", "10-25", "25-50", "50-100"]),
            directors=[{"name": f"Director {i+6}", "position": "Owner"}],
            last_updated=datetime.now(),
            is_verified=random.choice([True, False]),
            verification_score=random.randint(50, 100)
        )
        
        db.add(business)
    
    db.commit()
    print(f"Created {count} sample businesses")

def create_sample_users(db: Session):
    """Create sample user accounts"""
    print("Creating sample users...")
    
    # Test user (free plan)
    test_user = User(
        email="test@example.com",
        full_name="Test User",
        company="Test Company",
        hashed_password=get_password_hash("password123"),
        api_key="test_api_key_1234567890",
        plan=UserPlan.FREE,
        daily_limit=100,
        monthly_limit=3000,
        is_active=True,
        is_verified=True,
        verified_at=datetime.now()
    )
    db.add(test_user)
    
    # Pro user
    pro_user = User(
        email="pro@example.com",
        full_name="Pro User",
        company="Pro Solutions Ltd",
        hashed_password=get_password_hash("password123"),
        api_key=generate_api_key(),
        plan=UserPlan.PRO,
        daily_limit=10000,
        monthly_limit=300000,
        is_active=True,
        is_verified=True,
        verified_at=datetime.now()
    )
    db.add(pro_user)
    
    # Business user
    business_user = User(
        email="business@example.com",
        full_name="Business User",
        company="Enterprise Corp",
        hashed_password=get_password_hash("password123"),
        api_key=generate_api_key(),
        plan=UserPlan.BUSINESS,
        daily_limit=100000,
        monthly_limit=3000000,
        is_active=True,
        is_verified=True,
        verified_at=datetime.now()
    )
    db.add(business_user)
    
    db.commit()
    print("Created sample users")
    print(f"Test user API key: {test_user.api_key}")
    print(f"Pro user API key: {pro_user.api_key}")
    print(f"Business user API key: {business_user.api_key}")

def main():
    """Main function to create sample data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create sample data
        create_sample_users(db)
        create_sample_businesses(db, count=50)
        
        print("\n✅ Sample data created successfully!")
        print("\nYou can now:")
        print("1. Run the API: uvicorn app.main:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Use API key: test_api_key_1234567890")
        print("\nSample endpoints:")
        print("- GET /api/v1/businesses/")
        print("- GET /api/v1/businesses/search?q=brewery")
        print("- GET /api/v1/businesses/1")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()