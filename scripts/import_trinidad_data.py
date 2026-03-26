#!/usr/bin/env python3
"""
Import Trinidad business data into CaribAPI database
"""
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.business import Business
from app.models.base import Base
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_from_json(filename: str = "trinidad_businesses.json"):
    """Import business data from JSON file"""
    logger.info(f"Importing data from {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"File {filename} not found. Run scrape_trinidad.py first.")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {str(e)}")
        return
    
    if not data:
        logger.error("No data found in file.")
        return
    
    db = SessionLocal()
    imported = 0
    updated = 0
    errors = 0
    
    try:
        for business_data in data:
            try:
                # Convert registration_date string to datetime if needed
                if 'registration_date' in business_data and isinstance(business_data['registration_date'], str):
                    try:
                        business_data['registration_date'] = datetime.strptime(
                            business_data['registration_date'], '%Y-%m-%d'
                        )
                    except ValueError:
                        # If date format is different, use today's date
                        business_data['registration_date'] = datetime.now()
                
                # Ensure last_updated is datetime
                if 'last_updated' in business_data:
                    if isinstance(business_data['last_updated'], str):
                        try:
                            business_data['last_updated'] = datetime.strptime(
                                business_data['last_updated'], '%Y-%m-%d'
                            )
                        except ValueError:
                            business_data['last_updated'] = datetime.now()
                else:
                    business_data['last_updated'] = datetime.now()
                
                # Check if business already exists
                existing = db.query(Business).filter(
                    Business.registration_number == business_data['registration_number']
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in business_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    updated += 1
                    logger.debug(f"Updated: {business_data['registration_number']}")
                else:
                    # Create new record
                    business = Business(**business_data)
                    db.add(business)
                    imported += 1
                    logger.debug(f"Imported: {business_data['registration_number']}")
                
            except Exception as e:
                errors += 1
                logger.error(f"Error processing {business_data.get('registration_number', 'unknown')}: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"✅ Import complete: {imported} new, {updated} updated, {errors} errors")
        
        # Show summary
        total_in_db = db.query(Business).count()
        logger.info(f"Total businesses in database: {total_in_db}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Database error: {str(e)}")
    finally:
        db.close()

def create_tables_if_not_exist():
    """Create database tables if they don't exist"""
    logger.info("Checking/Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables ready")

def show_database_stats():
    """Show current database statistics"""
    db = SessionLocal()
    try:
        total = db.query(Business).count()
        by_city = db.query(Business.city, db.func.count(Business.id)).group_by(Business.city).all()
        by_industry = db.query(Business.industry, db.func.count(Business.id)).group_by(Business.industry).all()
        by_status = db.query(Business.status, db.func.count(Business.id)).group_by(Business.status).all()
        
        logger.info("=" * 60)
        logger.info("Database Statistics:")
        logger.info("=" * 60)
        logger.info(f"Total businesses: {total}")
        
        logger.info("\nBy City (top 10):")
        for city, count in sorted(by_city, key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {city}: {count}")
        
        logger.info("\nBy Industry (top 10):")
        for industry, count in sorted(by_industry, key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {industry}: {count}")
        
        logger.info("\nBy Status:")
        for status, count in sorted(by_status, key=lambda x: x[1], reverse=True):
            logger.info(f"  {status}: {count}")
            
    finally:
        db.close()

def main():
    """Main import function"""
    print("=" * 60)
    print("CaribAPI - Trinidad Business Data Import")
    print("=" * 60)
    
    # Check if data file exists
    data_file = "trinidad_businesses.json"
    if not os.path.exists(data_file):
        print(f"❌ Data file '{data_file}' not found.")
        print("\nFirst, generate sample data:")
        print("  python scripts/scrape_trinidad.py")
        print("\nOr create your own data file with Trinidad business records.")
        return
    
    # Create tables if needed
    create_tables_if_not_exist()
    
    # Import data
    import_from_json(data_file)
    
    # Show statistics
    show_database_stats()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Test the API with real data:")
    print("   curl -H 'X-API-Key: test_api_key_1234567890' \\")
    print("     http://localhost:8000/api/v1/businesses/")
    print("\n2. Add more countries:")
    print("   - Jamaica: Companies Office of Jamaica")
    print("   - Barbados: Corporate Affairs Registry")
    print("   - Bahamas: Registrar General's Department")
    print("\n3. Set up automated updates:")
    print("   - Schedule daily scraping with cron")
    print("   - Add error notifications")
    print("   - Monitor data quality")

if __name__ == "__main__":
    main()