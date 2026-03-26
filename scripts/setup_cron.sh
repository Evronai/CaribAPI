#!/bin/bash

# CaribAPI Cron Setup Script
# Sets up automated daily updates for business data

set -e

echo "🚀 Setting up CaribAPI Automated Updates"
echo "=========================================="

# Check if running as root (for system cron)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root. Setting up system cron job."
    CRON_USER="root"
    CRON_FILE="/etc/cron.d/caribapi"
else
    echo "Setting up user cron job."
    CRON_USER="$USER"
    CRON_FILE="/tmp/caribapi_cron"
fi

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Project directory: $PROJECT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
VENV_DIR="$PROJECT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment not found at $VENV_DIR"
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    echo "Installing dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install -r "$PROJECT_DIR/requirements.txt"
    deactivate
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found at $VENV_DIR"
fi

# Create logs directory
LOGS_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOGS_DIR"
echo "✅ Logs directory: $LOGS_DIR"

# Create data directory
DATA_DIR="$PROJECT_DIR/data"
mkdir -p "$DATA_DIR"
echo "✅ Data directory: $DATA_DIR"

# Create the cron job entry
CRON_JOB="0 2 * * * $CRON_USER cd $PROJECT_DIR && $VENV_DIR/bin/python scripts/automated_update.py >> $LOGS_DIR/cron.log 2>&1"

echo ""
echo "📋 Cron Job Configuration:"
echo "=========================="
echo "Schedule: Daily at 2:00 AM"
echo "Command: cd $PROJECT_DIR && $VENV_DIR/bin/python scripts/automated_update.py"
echo "Logs: $LOGS_DIR/cron.log"
echo ""
echo "Full cron entry:"
echo "$CRON_JOB"
echo ""

# Ask for confirmation
read -p "Do you want to install this cron job? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ "$EUID" -eq 0 ]; then
        # System cron
        echo "$CRON_JOB" | sudo tee "$CRON_FILE" > /dev/null
        sudo chmod 644 "$CRON_FILE"
        echo "✅ System cron job installed at $CRON_FILE"
    else
        # User cron
        (crontab -l 2>/dev/null | grep -v "automated_update.py"; echo "$CRON_JOB") | crontab -
        echo "✅ User cron job installed"
    fi
    
    # Also add a weekly cleanup job
    CLEANUP_JOB="0 3 * * 0 $CRON_USER find $LOGS_DIR -name '*.log' -mtime +30 -delete && find $DATA_DIR -name '*.json' -mtime +14 -delete"
    
    if [ "$EUID" -eq 0 ]; then
        echo "$CLEANUP_JOB" | sudo tee -a "$CRON_FILE" > /dev/null
    else
        (crontab -l 2>/dev/null; echo "$CLEANUP_JOB") | crontab -
    fi
    
    echo "✅ Cleanup job added (weekly log rotation)"
    
else
    echo "❌ Cron job not installed."
    echo ""
    echo "You can manually add this to your crontab:"
    echo "crontab -e"
    echo ""
    echo "Then add this line:"
    echo "$CRON_JOB"
    exit 0
fi

# Test the setup
echo ""
echo "🧪 Testing the setup..."
echo "======================"

# Create a test script
TEST_SCRIPT="$PROJECT_DIR/scripts/test_cron_setup.py"
cat > "$TEST_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
Test script for cron setup
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automated_update import AutomatedUpdate

def test():
    print("Testing CaribAPI automated update system...")
    
    updater = AutomatedUpdate()
    
    # Test configuration
    print(f"Project root: {updater.project_root}")
    print(f"Data directory: {updater.data_dir}")
    print(f"Log directory: logs/")
    
    # Check if scraper exists
    scraper_path = os.path.join(updater.project_root, "scripts", "scrape_yellowpages.py")
    if os.path.exists(scraper_path):
        print("✅ Scraper script found")
    else:
        print("❌ Scraper script not found")
        return False
    
    # Check if import script exists
    import_path = os.path.join(updater.project_root, "scripts", "import_trinidad_data.py")
    if os.path.exists(import_path):
        print("✅ Import script found")
    else:
        print("❌ Import script not found")
        return False
    
    # Check virtual environment
    venv_path = os.path.join(updater.project_root, "venv")
    if os.path.exists(venv_path):
        print("✅ Virtual environment found")
        
        # Check Python in venv
        venv_python = os.path.join(venv_path, "bin", "python")
        if os.path.exists(venv_python):
            print("✅ Python executable in venv found")
        else:
            print("❌ Python executable not found in venv")
            return False
    else:
        print("⚠️  Virtual environment not found (will use system Python)")
    
    print("\n✅ All checks passed!")
    print("\nThe automated update system is ready.")
    print("It will run daily at 2:00 AM and:")
    print("1. Scrape new business data")
    print("2. Import to database")
    print("3. Clean up old files")
    print("4. Log results to logs/ directory")
    
    return True

if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)
EOF

chmod +x "$TEST_SCRIPT"

# Run the test
if "$VENV_DIR/bin/python" "$TEST_SCRIPT"; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. The system will run automatically at 2:00 AM daily"
    echo "2. Check logs in: $LOGS_DIR/"
    echo "3. Check data in: $DATA_DIR/"
    echo "4. To run manually: cd $PROJECT_DIR && $VENV_DIR/bin/python scripts/automated_update.py"
    echo ""
    echo "To view cron jobs:"
    if [ "$EUID" -eq 0 ]; then
        echo "  sudo cat $CRON_FILE"
    else
        echo "  crontab -l"
    fi
    echo ""
    echo "To remove cron jobs:"
    if [ "$EUID" -eq 0 ]; then
        echo "  sudo rm $CRON_FILE"
    else
        echo "  crontab -e  # Remove the CaribAPI lines"
    fi
else
    echo ""
    echo "⚠️  Setup test failed. Please check the errors above."
    exit 1
fi

# Clean up test script
rm "$TEST_SCRIPT"

echo ""
echo "✅ CaribAPI automated updates are now configured!"
echo "   Your business data will stay fresh automatically. 🚀"