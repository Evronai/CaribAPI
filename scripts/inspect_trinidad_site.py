#!/usr/bin/env python3
"""
Inspect Trinidad Companies Registry website structure
"""
import requests
from bs4 import BeautifulSoup
import time
import json

def check_website_access():
    """Check if we can access the Trinidad Companies Registry"""
    print("🔍 Inspecting Trinidad Companies Registry Website")
    print("=" * 60)
    
    # Possible URLs to check
    urls_to_check = [
        "https://www.ctt.org.tt/",
        "https://ctt.org.tt/",
        "http://www.ctt.org.tt/",
        "http://ctt.org.tt/",
        "https://companies-registry.gov.tt/",
        "https://www.companies.gov.tt/",
    ]
    
    for url in urls_to_check:
        print(f"\nTrying: {url}")
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            print(f"  Status: {response.status_code}")
            print(f"  Final URL: {response.url}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for company search elements
                search_forms = soup.find_all('form')
                search_inputs = soup.find_all('input', {'type': 'text', 'type': 'search'})
                company_keywords = ['company', 'search', 'registry', 'business', 'register']
                
                print(f"  Forms found: {len(search_forms)}")
                print(f"  Search inputs: {len(search_inputs)}")
                
                # Check page title and headings
                title = soup.title.string if soup.title else "No title"
                print(f"  Title: {title[:50]}...")
                
                # Look for company search links
                for keyword in company_keywords:
                    links = soup.find_all('a', string=lambda text: text and keyword.lower() in text.lower())
                    if links:
                        print(f"  Found '{keyword}' links: {len(links)}")
                        for link in links[:2]:
                            print(f"    - {link.get('href', 'No href')}")
                
                # Save sample HTML for inspection
                with open('website_sample.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup.prettify())[:5000])
                print("  ✅ Saved sample HTML to website_sample.html")
                
                return url, soup
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error: {str(e)}")
            continue
    
    print("\n❌ Could not access Trinidad Companies Registry website")
    print("\nAlternative data sources:")
    print("1. Trinidad & Tobago Yellow Pages: https://yellowpages.tt/")
    print("2. Trinidad Chamber of Commerce: https://chamber.org.tt/")
    print("3. OpenStreetMap business data")
    print("4. Manual data entry from public records")
    
    return None, None

def analyze_search_functionality(soup):
    """Analyze search functionality if available"""
    print("\n🔎 Analyzing Search Functionality")
    print("=" * 60)
    
    if not soup:
        print("No HTML to analyze")
        return
    
    # Look for search forms
    forms = soup.find_all('form')
    print(f"Total forms: {len(forms)}")
    
    for i, form in enumerate(forms[:3]):  # Check first 3 forms
        print(f"\nForm {i+1}:")
        print(f"  Action: {form.get('action', 'No action')}")
        print(f"  Method: {form.get('method', 'GET')}")
        
        # Find all inputs
        inputs = form.find_all('input')
        print(f"  Inputs: {len(inputs)}")
        
        for inp in inputs:
            name = inp.get('name', 'No name')
            input_type = inp.get('type', 'text')
            placeholder = inp.get('placeholder', '')
            print(f"    - {name} ({input_type}): {placeholder}")
    
    # Look for company data tables
    tables = soup.find_all('table')
    print(f"\nTotal tables: {len(tables)}")
    
    for i, table in enumerate(tables[:2]):  # Check first 2 tables
        print(f"\nTable {i+1}:")
        headers = table.find_all('th')
        if headers:
            print(f"  Headers: {[h.get_text(strip=True) for h in headers[:5]]}")
        else:
            # Check for header cells in first row
            first_row = table.find('tr')
            if first_row:
                cells = first_row.find_all(['td', 'th'])
                print(f"  First row: {[c.get_text(strip=True) for c in cells[:5]]}")

def check_for_api():
    """Check if there's an API available"""
    print("\n🔌 Checking for API Access")
    print("=" * 60)
    
    # Common API endpoints to check
    api_endpoints = [
        "/api/",
        "/api/v1/",
        "/search/json",
        "/companies/json",
        "/data/",
    ]
    
    base_urls = [
        "https://www.ctt.org.tt",
        "https://ctt.org.tt",
        "https://data.gov.tt",
    ]
    
    for base_url in base_urls:
        print(f"\nChecking {base_url}:")
        for endpoint in api_endpoints:
            url = base_url + endpoint
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        print(f"  ✅ Found JSON API: {url}")
                        try:
                            data = response.json()
                            print(f"     Sample keys: {list(data.keys())[:5]}")
                        except:
                            print(f"     Could not parse JSON")
                    elif 'xml' in content_type:
                        print(f"  ⚠️ Found XML endpoint: {url}")
                    else:
                        print(f"  ⚠️ Found endpoint: {url} ({content_type})")
            except:
                continue

def generate_scraping_plan():
    """Generate a scraping plan based on findings"""
    print("\n📋 Scraping Implementation Plan")
    print("=" * 60)
    
    print("Based on typical government registry websites:")
    print("\n1. **Search Form Analysis:**")
    print("   - Find the company search form")
    print("   - Identify input field names")
    print("   - Determine form submission method")
    
    print("\n2. **Search Strategy:**")
    print("   - Start with common business names")
    print("   - Search by registration number ranges")
    print("   - Use alphabetical search (A-Z)")
    print("   - Search by industry/category")
    
    print("\n3. **Data Extraction:**")
    print("   - Parse search results table")
    print("   - Extract company details page URLs")
    print("   - Scrape individual company pages")
    print("   - Handle pagination")
    
    print("\n4. **Rate Limiting:**")
    print("   - Add delays between requests (3-5 seconds)")
    print("   - Respect robots.txt")
    print("   - Use rotating user agents")
    print("   - Implement error handling")
    
    print("\n5. **Data Storage:**")
    print("   - Save raw HTML for debugging")
    print("   - Extract structured data to JSON")
    print("   - Update database incrementally")
    print("   - Track scraping progress")

def main():
    """Main inspection function"""
    print("🚀 Trinidad Companies Registry Website Inspector")
    print("=" * 60)
    
    # Check website access
    url, soup = check_website_access()
    
    if url and soup:
        # Analyze what we found
        analyze_search_functionality(soup)
        
        # Check for API
        check_for_api()
        
        # Generate scraping plan
        generate_scraping_plan()
        
        print("\n" + "=" * 60)
        print("🎯 Next Steps:")
        print("=" * 60)
        print("1. Review website_sample.html")
        print("2. Identify search form structure")
        print("3. Write targeted scraper for that form")
        print("4. Test with small searches first")
        print("5. Scale up gradually")
        
    else:
        print("\n" + "=" * 60)
        print("⚠️  Alternative Approach Needed")
        print("=" * 60)
        print("Since we can't access the official registry directly:")
        print("\n1. **Use Alternative Sources:**")
        print("   - Trinidad Yellow Pages (yellowpages.tt)")
        print("   - Business directories")
        print("   - LinkedIn company pages")
        print("   - News articles about Trinidad businesses")
        
        print("\n2. **Manual Data Entry:**")
        print("   - Start with 50-100 known large companies")
        print("   - Add SMEs gradually")
        print("   - Crowdsource from users")
        
        print("\n3. **Partner Approach:**")
        print("   - Contact Trinidad Chamber of Commerce")
        print("   - Partner with local business associations")
        print("   - License data from commercial providers")

if __name__ == "__main__":
    main()