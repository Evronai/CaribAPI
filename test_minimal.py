#!/usr/bin/env python3
"""
Minimal test of CaribAPI without database dependencies
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="CaribAPI Test",
    description="Caribbean Business Data API - Test Version",
    version="1.0.0"
)

# Sample business data
SAMPLE_BUSINESSES = [
    {
        "id": 1,
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
        "status": "Active",
        "annual_revenue_range": "$5M-$10M",
        "employee_count_range": "100-250"
    },
    {
        "id": 2,
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
        "status": "Active",
        "annual_revenue_range": "$1M-$5M",
        "employee_count_range": "50-100"
    },
    {
        "id": 3,
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
        "status": "Active",
        "annual_revenue_range": "$500K-$1M",
        "employee_count_range": "25-50"
    }
]

# Pydantic models
class Business(BaseModel):
    id: int
    name: str
    registration_number: str
    city: str
    industry: str
    status: str

class BusinessDetail(BaseModel):
    id: int
    name: str
    registration_number: str
    address: str
    city: str
    region: str
    phone: str
    email: str
    website: str
    business_type: str
    industry: str
    status: str
    annual_revenue_range: str
    employee_count_range: str

# Authentication middleware
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "test_api_key_1234567890":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CaribAPI Test", "version": "1.0.0"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to CaribAPI - Caribbean Business Data Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "businesses": "/api/v1/businesses/",
            "search": "/api/v1/businesses/search?q={query}",
            "business_by_id": "/api/v1/businesses/{id}"
        }
    }

# Get all businesses
@app.get("/api/v1/businesses/", response_model=List[Business])
async def get_businesses(
    city: Optional[str] = None,
    industry: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    filtered = SAMPLE_BUSINESSES
    if city:
        filtered = [b for b in filtered if b["city"].lower() == city.lower()]
    if industry:
        filtered = [b for b in filtered if b["industry"].lower() == industry.lower()]
    
    return filtered

# Search businesses
@app.get("/api/v1/businesses/search", response_model=List[Business])
async def search_businesses(
    q: str,
    api_key: str = Depends(verify_api_key)
):
    results = []
    query = q.lower()
    
    for business in SAMPLE_BUSINESSES:
        if (query in business["name"].lower() or 
            query in business["registration_number"].lower() or
            query in business["city"].lower() or
            query in business["industry"].lower()):
            results.append(business)
    
    return results

# Get business by ID
@app.get("/api/v1/businesses/{business_id}", response_model=BusinessDetail)
async def get_business(
    business_id: int,
    api_key: str = Depends(verify_api_key)
):
    for business in SAMPLE_BUSINESSES:
        if business["id"] == business_id:
            return business
    
    raise HTTPException(status_code=404, detail="Business not found")

# Business statistics
@app.get("/api/v1/businesses/stats/summary")
async def business_stats(api_key: str = Depends(verify_api_key)):
    total = len(SAMPLE_BUSINESSES)
    by_city = {}
    by_industry = {}
    by_status = {}
    
    for business in SAMPLE_BUSINESSES:
        city = business["city"]
        industry = business["industry"]
        status = business["status"]
        
        by_city[city] = by_city.get(city, 0) + 1
        by_industry[industry] = by_industry.get(industry, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
    
    return {
        "total_businesses": total,
        "by_city": by_city,
        "by_industry": by_industry,
        "by_status": by_status
    }

if __name__ == "__main__":
    print("🚀 Starting CaribAPI Test Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔑 Test API Key: test_api_key_1234567890")
    print("\nSample endpoints:")
    print("- GET /api/v1/businesses/")
    print("- GET /api/v1/businesses/search?q=brewery")
    print("- GET /api/v1/businesses/1")
    print("- GET /api/v1/businesses/stats/summary")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)