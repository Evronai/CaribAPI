#!/usr/bin/env python3
"""
Test the CaribAPI endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"
API_KEY = "test_api_key_1234567890"  # From sample data

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print("\nTesting root endpoint...")
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_businesses():
    """Test businesses endpoint"""
    print("\nTesting businesses endpoint...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/api/v1/businesses/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} businesses")
        if data:
            print(f"First business: {data[0]['name']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_search_businesses():
    """Test search endpoint"""
    print("\nTesting search endpoint...")
    headers = {"X-API-Key": API_KEY}
    params = {"q": "brewery"}
    response = requests.get(f"{BASE_URL}/api/v1/businesses/search", headers=headers, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} businesses matching 'brewery'")
        if data:
            for business in data[:3]:  # Show first 3
                print(f"  - {business['name']} ({business['city']})")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_get_business_by_id():
    """Test get business by ID"""
    print("\nTesting get business by ID...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/api/v1/businesses/1", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        business = response.json()
        print(f"Business: {business['name']}")
        print(f"Registration: {business['registration_number']}")
        print(f"City: {business['city']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_business_stats():
    """Test business statistics"""
    print("\nTesting business statistics...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/api/v1/businesses/stats/summary", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Total businesses: {stats['total_businesses']}")
        print(f"By status: {stats['by_status']}")
        print(f"Top cities: {list(stats['by_city'].keys())[:3]}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_rate_limiting():
    """Test rate limiting"""
    print("\nTesting rate limiting...")
    headers = {"X-API-Key": API_KEY}
    
    # Make multiple requests quickly
    for i in range(5):
        response = requests.get(f"{BASE_URL}/api/v1/businesses/", headers=headers)
        print(f"Request {i+1}: Status {response.status_code}")
    
    # Check usage
    response = requests.get(f"{BASE_URL}/api/v1/auth/usage", headers=headers)
    if response.status_code == 200:
        usage = response.json()
        print(f"\nUsage stats:")
        print(f"  Plan: {usage['plan']}")
        print(f"  Used today: {usage['usage']['today']}")
        print(f"  Daily limit: {usage['limits']['daily']}")
        print(f"  Remaining today: {usage['remaining']['daily']}")
    
    return True

def test_without_api_key():
    """Test access without API key"""
    print("\nTesting access without API key...")
    response = requests.get(f"{BASE_URL}/api/v1/businesses/")
    print(f"Status: {response.status_code} (should be 401)")
    
    if response.status_code == 401:
        print("✓ Correctly rejected unauthorized access")
        return True
    else:
        print(f"Unexpected: {response.text}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CaribAPI Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Unauthorized Access", test_without_api_key),
        ("Get Businesses", test_get_businesses),
        ("Search Businesses", test_search_businesses),
        ("Get Business by ID", test_get_business_by_id),
        ("Business Statistics", test_business_stats),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✓' if success else '✗'} {test_name}\n")
        except Exception as e:
            print(f"✗ {test_name} - Error: {str(e)}\n")
            results.append((test_name, False))
    
    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status:6} {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n✅ All tests passed! API is working correctly.")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/docs for API documentation")
        print("2. Use API key: test_api_key_1234567890")
        print("3. Try the endpoints in the documentation")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()