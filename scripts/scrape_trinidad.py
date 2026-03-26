#!/usr/bin/env python3
"""
Scrape Trinidad & Tobago business data from public sources
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict
import csv

class TrinidadBusinessScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_companies_registry(self, limit: int = 100) -> List[Dict]:
        """
        Scrape sample data from Trinidad Companies Registry
        Note: This is a template. Actual scraping would need to adapt to the real website structure.
        """
        print(f"Scraping Trinidad business data (sample: {limit} records)...")
        
        # Sample data - in reality, you'd scrape from:
        # https://www.ctt.org.tt/company-search/
        # Or use their API if available
        
        sample_companies = []
        
        # Trinidad business sectors
        sectors = [
            "Energy", "Finance", "Manufacturing", "Retail", "Tourism",
            "Construction", "Transportation", "Agriculture", "Technology", "Healthcare"
        ]
        
        # Trinidad cities
        cities = [
            "Port of Spain", "San Fernando", "Chaguanas", "Arima", "Point Fortin",
            "Tunapuna", "Scarborough", "Diego Martin", "Couva", "Princes Town"
        ]
        
        for i in range(1, limit + 1):
            sector = random.choice(sectors)
            city = random.choice(cities)
            
            company = {
                "registration_number": f"TRN{20230000 + i}",
                "name": f"{sector} Company {i} Ltd",
                "business_type": random.choice(["Limited Liability", "Sole Proprietor", "Partnership", "Corporation"]),
                "registered_address": f"{random.randint(1, 999)} {random.choice(['Main Road', 'Independence Square', 'Ariapita Avenue', 'Wrightson Road'])}",
                "city": city,
                "region": city,
                "country": "Trinidad and Tobago",
                "phone": f"+1-868-{random.randint(600, 699)}-{random.randint(1000, 9999)}",
                "email": f"info@company{i}.com",
                "website": f"https://company{i}.com",
                "industry": sector,
                "sub_industry": f"{sector} Services",
                "status": random.choice(["Active", "Active", "Active", "Inactive", "Dissolved"]),
                "registration_date": f"2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "annual_revenue_range": random.choice([
                    "$50K-$100K", "$100K-$250K", "$250K-$500K", "$500K-$1M",
                    "$1M-$5M", "$5M-$10M", "$10M-$50M"
                ]),
                "employee_count_range": random.choice([
                    "1-10", "10-25", "25-50", "50-100", "100-250", "250-500"
                ]),
                "directors": [
                    {
                        "name": f"Director {i}",
                        "position": random.choice(["Managing Director", "CEO", "Director", "Owner"])
                    }
                ],
                "is_verified": random.choice([True, False]),
                "verification_score": random.randint(50, 100),
                "last_updated": "2024-01-15"
            }
            
            sample_companies.append(company)
            
            if i % 10 == 0:
                print(f"  Generated {i}/{limit} sample records...")
        
        print(f"✅ Generated {len(sample_companies)} sample Trinidad business records")
        return sample_companies
    
    def scrape_actual_website(self, search_term: str = "") -> List[Dict]:
        """
        Actual scraping function for Trinidad Companies Registry
        This needs to be adapted based on the actual website structure
        """
        print(f"Attempting to scrape actual Trinidad Companies Registry...")
        
        try:
            # Example URL - would need to find actual search endpoint
            url = "https://www.ctt.org.tt/company-search/"
            
            # Try to access the website
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # This is where you'd parse the actual HTML structure
                # The actual parsing code depends on the website structure
                
                print("✅ Successfully accessed Trinidad Companies Registry")
                print("⚠️  Note: Actual parsing code needs to be written based on website structure")
                
                # For now, return empty and use sample data
                return []
                
            else:
                print(f"❌ Could not access website. Status: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error scraping website: {str(e)}")
            return []
    
    def save_to_json(self, data: List[Dict], filename: str = "trinidad_businesses.json"):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(data)} records to {filename}")
    
    def save_to_csv(self, data: List[Dict], filename: str = "trinidad_businesses.csv"):
        """Save scraped data to CSV file"""
        if not data:
            return
            
        # Extract all possible field names
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        
        fieldnames = sorted(fieldnames)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                # Flatten nested structures
                flat_item = {}
                for key, value in item.items():
                    if isinstance(value, (list, dict)):
                        flat_item[key] = json.dumps(value)
                    else:
                        flat_item[key] = value
                writer.writerow(flat_item)
        
        print(f"✅ Saved {len(data)} records to {filename}")
    
    def import_to_database(self, data: List[Dict]):
        """
        Import scraped data into CaribAPI database
        """
        print("Importing data to database...")
        
        # This would connect to your PostgreSQL database
        # and insert/update the business records
        
        # For now, just show what would be imported
        print(f"Would import {len(data)} business records")
        
        # Example of what the import code would look like:
        """
        from app.database import SessionLocal
        from app.models.business import Business
        
        db = SessionLocal()
        try:
            for business_data in data:
                # Check if business already exists
                existing = db.query(Business).filter(
                    Business.registration_number == business_data['registration_number']
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in business_data.items():
                        setattr(existing, key, value)
                else:
                    # Create new record
                    business = Business(**business_data)
                    db.add(business)
            
            db.commit()
            print(f"✅ Imported {len(data)} records to database")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error importing to database: {str(e)}")
        finally:
            db.close()
        """

def main():
    """Main function to run the scraper"""
    scraper = TrinidadBusinessScraper()
    
    print("=" * 60)
    print("Trinidad Business Data Scraper")
    print("=" * 60)
    
    # Try to scrape actual website first
    print("\n1. Attempting to scrape actual Trinidad Companies Registry...")
    actual_data = scraper.scrape_actual_website()
    
    if actual_data:
        print(f"✅ Found {len(actual_data)} actual business records")
        data_to_save = actual_data
    else:
        print("⚠️  Using sample data (actual scraping needs website-specific code)")
        
        # Generate sample data
        print("\n2. Generating sample Trinidad business data...")
        sample_data = scraper.scrape_companies_registry(limit=50)
        data_to_save = sample_data
    
    # Save data
    print("\n3. Saving data...")
    scraper.save_to_json(data_to_save, "trinidad_businesses.json")
    scraper.save_to_csv(data_to_save, "trinidad_businesses.csv")
    
    # Show import instructions
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Review the scraped data:")
    print("   - cat trinidad_businesses.json | head -5")
    print("   - wc -l trinidad_businesses.csv")
    print("\n2. Import to CaribAPI database:")
    print("   python scripts/import_trinidad_data.py")
    print("\n3. Update the scraper for actual website:")
    print("   - Inspect https://www.ctt.org.tt/company-search/")
    print("   - Update scrape_actual_website() method")
    print("   - Test with actual search terms")
    print("\n4. Set up automated scraping:")
    print("   - Schedule with cron: 0 2 * * * (daily at 2 AM)")
    print("   - Add error handling and logging")
    print("   - Implement rate limiting")

if __name__ == "__main__":
    main()