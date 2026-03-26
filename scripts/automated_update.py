#!/usr/bin/env python3
"""
Automated daily update system for CaribAPI
Runs scraping, imports data, and sends notifications
"""
import sys
import os
import json
import logging
from datetime import datetime, timedelta
import subprocess
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"update_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedUpdate:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Configuration
        self.config = {
            "scrape_enabled": True,
            "import_enabled": True,
            "notify_enabled": False,  # Set to True when you have notification setup
            "max_records_per_run": 100,
            "backup_days": 7,
        }
    
    def run_scraping(self) -> Dict[str, Any]:
        """Run the scraping process"""
        logger.info("Starting scraping process...")
        
        try:
            # Run the scraper
            scraper_script = os.path.join(self.project_root, "scripts", "scrape_yellowpages.py")
            result = subprocess.run(
                [sys.executable, scraper_script],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("✅ Scraping completed successfully")
                
                # Parse output to find generated files
                output = result.stdout
                json_file = None
                
                for line in output.split('\n'):
                    if "Saved" in line and ".json" in line:
                        # Extract filename
                        parts = line.split()
                        for part in parts:
                            if part.endswith('.json'):
                                json_file = part
                                break
                
                if json_file and os.path.exists(json_file):
                    # Load the data to get stats
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    stats = {
                        "file": json_file,
                        "record_count": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "status": "success"
                    }
                    
                    # Move to data directory
                    dest_file = os.path.join(self.data_dir, os.path.basename(json_file))
                    os.rename(json_file, dest_file)
                    stats["file"] = dest_file
                    
                    logger.info(f"Scraped {len(data)} records, saved to {dest_file}")
                    return stats
                else:
                    logger.warning("Could not find generated JSON file")
                    return {"status": "warning", "message": "No data file found"}
                    
            else:
                logger.error(f"❌ Scraping failed: {result.stderr}")
                return {"status": "error", "message": result.stderr}
                
        except Exception as e:
            logger.error(f"❌ Scraping error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_import(self, data_file: str = None) -> Dict[str, Any]:
        """Import data into database"""
        logger.info("Starting data import process...")
        
        try:
            # If no specific file, use the latest
            if not data_file:
                latest_file = "trinidad_businesses_latest.json"
                if os.path.exists(latest_file):
                    data_file = latest_file
                else:
                    # Find the most recent data file
                    json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
                    if json_files:
                        json_files.sort(reverse=True)
                        data_file = os.path.join(self.data_dir, json_files[0])
                    else:
                        logger.error("No data files found for import")
                        return {"status": "error", "message": "No data files"}
            
            # Run the import script
            import_script = os.path.join(self.project_root, "scripts", "import_trinidad_data.py")
            
            result = subprocess.run(
                [sys.executable, import_script, "--file", data_file],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("✅ Data import completed successfully")
                
                # Parse import statistics from output
                output = result.stdout
                stats = {
                    "file": data_file,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "output": output[-500:]  # Last 500 chars of output
                }
                
                return stats
            else:
                logger.error(f"❌ Import failed: {result.stderr}")
                return {"status": "error", "message": result.stderr}
                
        except Exception as e:
            logger.error(f"❌ Import error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def cleanup_old_files(self):
        """Clean up old data files"""
        logger.info("Cleaning up old files...")
        
        try:
            # Remove files older than backup_days
            cutoff_date = datetime.now() - timedelta(days=self.config["backup_days"])
            
            files_removed = 0
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json') or filename.endswith('.csv'):
                    filepath = os.path.join(self.data_dir, filename)
                    
                    # Get file modification time
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if mtime < cutoff_date:
                        os.remove(filepath)
                        files_removed += 1
                        logger.debug(f"Removed old file: {filename}")
            
            logger.info(f"Cleaned up {files_removed} old files")
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
    
    def send_notification(self, scrape_stats: Dict, import_stats: Dict):
        """Send notification about update status"""
        if not self.config["notify_enabled"]:
            return
        
        logger.info("Sending notification...")
        
        # This is where you would integrate with:
        # - Email (SMTP)
        # - Slack/Discord webhook
        # - Telegram bot
        # - etc.
        
        # Example email notification (commented out)
        """
        import smtplib
        from email.mime.text import MIMEText
        
        subject = f"CaribAPI Daily Update - {datetime.now().strftime('%Y-%m-%d')}"
        
        if scrape_stats["status"] == "success" and import_stats["status"] == "success":
            body = f"✅ Daily update successful!\n\n"
            body += f"Scraped: {scrape_stats.get('record_count', 0)} records\n"
            body += f"Imported: Successfully\n"
            body += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        else:
            body = f"❌ Daily update failed!\n\n"
            body += f"Scrape status: {scrape_stats.get('status', 'unknown')}\n"
            body += f"Import status: {import_stats.get('status', 'unknown')}\n"
            body += f"Errors: {scrape_stats.get('message', '')} {import_stats.get('message', '')}"
        
        # Send email logic here
        """
        
        logger.info("Notification would be sent here")
    
    def generate_report(self, scrape_stats: Dict, import_stats: Dict) -> str:
        """Generate a summary report"""
        report = f"CaribAPI Daily Update Report\n"
        report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 50 + "\n\n"
        
        # Scraping section
        report += "📊 Scraping Results:\n"
        if scrape_stats["status"] == "success":
            report += f"  ✅ Success: {scrape_stats.get('record_count', 0)} records scraped\n"
            report += f"  File: {os.path.basename(scrape_stats.get('file', ''))}\n"
        else:
            report += f"  ❌ Failed: {scrape_stats.get('message', 'Unknown error')}\n"
        
        report += "\n"
        
        # Import section
        report += "🗃️  Import Results:\n"
        if import_stats["status"] == "success":
            report += f"  ✅ Success: Data imported to database\n"
            if "output" in import_stats:
                # Extract key info from output
                lines = import_stats["output"].split('\n')
                for line in lines:
                    if "imported" in line.lower() or "updated" in line.lower() or "error" in line.lower():
                        report += f"  {line.strip()}\n"
        else:
            report += f"  ❌ Failed: {import_stats.get('message', 'Unknown error')}\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += "Next scheduled update: Tomorrow 02:00\n"
        
        return report
    
    def run_full_update(self):
        """Run the complete update process"""
        logger.info("=" * 60)
        logger.info(f"Starting CaribAPI Daily Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        scrape_stats = {"status": "skipped", "message": "Scraping disabled"}
        import_stats = {"status": "skipped", "message": "Import disabled"}
        
        # Step 1: Scraping
        if self.config["scrape_enabled"]:
            scrape_stats = self.run_scraping()
        else:
            logger.info("Scraping disabled in config")
        
        # Step 2: Import
        if self.config["import_enabled"] and scrape_stats.get("status") == "success":
            import_stats = self.run_import(scrape_stats.get("file"))
        elif self.config["import_enabled"]:
            # Try import with latest file even if scraping failed
            import_stats = self.run_import()
        else:
            logger.info("Import disabled in config")
        
        # Step 3: Cleanup
        self.cleanup_old_files()
        
        # Step 4: Notifications
        self.send_notification(scrape_stats, import_stats)
        
        # Step 5: Generate and save report
        report = self.generate_report(scrape_stats, import_stats)
        
        report_file = os.path.join(log_dir, f"report_{datetime.now().strftime('%Y%m%d')}.txt")
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to {report_file}")
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("Update Summary:")
        logger.info(f"  Scraping: {scrape_stats.get('status', 'unknown')}")
        logger.info(f"  Import: {import_stats.get('status', 'unknown')}")
        logger.info(f"  Log file: {log_file}")
        logger.info(f"  Report file: {report_file}")
        logger.info("=" * 60)
        
        # Return overall status
        if scrape_stats.get("status") == "success" and import_stats.get("status") == "success":
            logger.info("✅ Daily update completed successfully!")
            return 0
        else:
            logger.warning("⚠️  Daily update completed with warnings/errors")
            return 1

def main():
    """Main function for automated updates"""
    updater = AutomatedUpdate()
    
    # You can override config via command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="CaribAPI Automated Update System")
    parser.add_argument("--no-scrape", action="store_true", help="Skip scraping")
    parser.add_argument("--no-import", action="store_true", help="Skip import")
    parser.add_argument("--file", help="Specific data file to import")
    
    args = parser.parse_args()
    
    if args.no_scrape:
        updater.config["scrape_enabled"] = False
    if args.no_import:
        updater.config["import_enabled"] = False
    
    # Run the update
    return updater.run_full_update()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)