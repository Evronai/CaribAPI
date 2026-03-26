#!/usr/bin/env python3
"""
Test CaribAPI with real(ish) Trinidad business data
"""
import json
import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "test_api_key_1234567890"
DATA_FILE = "trinidad_businesses.json"

def load_data():
    """Load Trinidad business data"""
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def test_api_with_real_data():
    """Test API endpoints with real data"""
    print("🚀 Testing CaribAPI with Trinidad Business Data")
    print("=" * 60)
    
    # Load data
    data = load_data()
    print(f"📊 Loaded {len(data)} Trinidad business records")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   ✅ Health: {response.json()}")
    except Exception as e:
        print(f"   ❌ Health check failed: {str(e)}")
        return
    
    # Test getting all businesses
    print("\n2. Testing get all businesses...")
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/businesses/", headers=headers, timeout=5)
        
        if response.status_code == 200:
            businesses = response.json()
            print(f"   ✅ Found {len(businesses)} businesses in API")
            if businesses:
                print(f"   📋 Sample: {businesses[0]['name']}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test search functionality
    print("\n3. Testing search...")
    try:
        # Search for energy companies (common in Trinidad)
        headers = {"X-API-Key": API_KEY}
        response = requests.get(
            f"{BASE_URL}/api/v1/businesses/search",
            headers=headers,
            params={"q": "energy"},
            timeout=5
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Found {len(results)} energy companies")
            if results:
                for biz in results[:3]:
                    print(f"     - {biz['name']} ({biz['city']})")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test filtering by city
    print("\n4. Testing filter by city...")
    try:
        # Get businesses in Port of Spain
        headers = {"X-API-Key": API_KEY}
        response = requests.get(
            f"{BASE_URL}/api/v1/businesses/",
            headers=headers,
            params={"city": "Port of Spain"},
            timeout=5
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Found {len(results)} businesses in Port of Spain")
            if results:
                print(f"     Sample industries: {', '.join(set(b['industry'] for b in results[:5]))}")
        else:
            print(f"   ❌ Filter failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test statistics
    print("\n5. Testing business statistics...")
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(
            f"{BASE_URL}/api/v1/businesses/stats/summary",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Statistics retrieved")
            print(f"     Total businesses: {stats['total_businesses']}")
            print(f"     Top cities: {list(stats['by_city'].keys())[:3]}")
            print(f"     Top industries: {list(stats['by_industry'].keys())[:3]}")
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Show data quality metrics
    print("\n" + "=" * 60)
    print("📈 Data Quality Analysis")
    print("=" * 60)
    
    # Analyze the loaded data
    total = len(data)
    active = sum(1 for b in data if b.get('status') == 'Active')
    verified = sum(1 for b in data if b.get('is_verified'))
    
    # Count by industry
    industries = {}
    cities = {}
    for business in data:
        industry = business.get('industry', 'Unknown')
        city = business.get('city', 'Unknown')
        
        industries[industry] = industries.get(industry, 0) + 1
        cities[city] = cities.get(city, 0) + 1
    
    print(f"Total records: {total}")
    print(f"Active businesses: {active} ({active/total*100:.1f}%)")
    print(f"Verified records: {verified} ({verified/total*100:.1f}%)")
    
    print(f"\nTop 5 Industries:")
    for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {industry}: {count} ({count/total*100:.1f}%)")
    
    print(f"\nTop 5 Cities:")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {city}: {count} ({count/total*100:.1f}%)")
    
    # Check data completeness
    required_fields = ['name', 'registration_number', 'city', 'industry', 'status']
    completeness = {}
    
    for field in required_fields:
        complete = sum(1 for b in data if field in b and b[field])
        completeness[field] = complete/total*100
    
    print(f"\nData Completeness:")
    for field, percent in completeness.items():
        print(f"  {field}: {percent:.1f}%")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps for Real Data:")
    print("=" * 60)
    print("1. Adapt scraper for actual Trinidad Companies Registry")
    print("2. Add more fields (director details, financials)")
    print("3. Implement data verification pipeline")
    print("4. Set up daily automated updates")
    print("5. Expand to other Caribbean countries")
    print("\n💡 Tip: Start with 100-200 high-quality records")
    print("   Quality > Quantity for initial customers")

if __name__ == "__main__":
    # First, check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            test_api_with_real_data()
        else:
            print("❌ CaribAPI is not running. Start it first:")
            print("   cd /home/frank/.openclaw/workspace/caribapi")
            print("   source test_venv/bin/activate")
            print("   python test_minimal.py")
    except requests.exceptions.ConnectionError:
        print("❌ CaribAPI is not running. Start it first:")
        print("   cd /home/frank/.openclaw/workspace/caribapi")
        print("   source test_venv/bin/activate")
        print("   python test_minimal.py")