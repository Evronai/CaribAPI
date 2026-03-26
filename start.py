#!/usr/bin/env python3
"""
Generic startup script for CaribAPI
Works on Render, Railway, Heroku, and local development
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("Installing from requirements.txt...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True, text=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e.stderr[:200]}")
            print("Attempting to continue anyway...")
    else:
        print("✅ All dependencies found")

def setup_environment():
    """Set up environment variables"""
    print("⚙️  Setting up environment...")
    
    # Check for required environment variables
    env_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'PORT': os.environ.get('PORT', '8000'),
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
    }
    
    print(f"Port: {env_vars['PORT']}")
    print(f"Database URL: {'Set' if env_vars['DATABASE_URL'] else 'Not set (using SQLite)'}")
    print(f"Secret Key: {'Set' if env_vars['SECRET_KEY'] else 'Not set (using default)'}")
    
    # Create minimal .env file if it doesn't exist (for local development)
    if not os.path.exists('.env') and not env_vars['DATABASE_URL']:
        print("Creating minimal .env file for local development...")
        with open('.env', 'w') as f:
            f.write("# Local development environment\n")
            f.write(f"SECRET_KEY={env_vars['SECRET_KEY'] or 'local-dev-secret-key-change-me'}\n")
            f.write("DATABASE_URL=sqlite:///./caribapi.db\n")
            f.write("ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000\n")
        print("✅ Created .env file")
    
    return env_vars

def initialize_database():
    """Initialize database if needed"""
    print("🗃️  Initializing database...")
    
    try:
        # Try to create tables and sample data
        result = subprocess.run(
            [sys.executable, 'scripts/create_sample_data.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database initialized")
            if result.stdout.strip():
                print(result.stdout[-300:])  # Last 300 chars
        else:
            print(f"⚠️  Database initialization had issues: {result.stderr[:300]}")
            print("Will start API anyway - may use SQLite or existing database")
            
    except Exception as e:
        print(f"⚠️  Database initialization error: {str(e)}")
        print("Will start API anyway")

def start_api(port):
    """Start the FastAPI application"""
    print(f"🚀 Starting CaribAPI on port {port}...")
    print("=" * 60)
    print("📡 API will be available at: http://localhost:8000 (local) or your deployment URL")
    print("📚 Documentation: /docs")
    print("🔑 Test API Key: test_api_key_1234567890")
    print("=" * 60)
    
    # Determine which app to run
    if os.path.exists('app/main.py'):
        # Use the full application
        import_command = 'app.main:app'
        print("✅ Using full CaribAPI application")
    else:
        # Use the minimal test app
        import_command = 'test_minimal:app'
        print("⚠️  Using minimal test API (full app not found)")
    
    # Start the server
    os.execvp('uvicorn', [
        'uvicorn', import_command,
        '--host', '0.0.0.0',
        '--port', str(port),
        '--reload' if os.environ.get('ENVIRONMENT') == 'development' else ''
    ])

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 CaribAPI Startup")
    print("=" * 60)
    
    try:
        # Setup
        check_dependencies()
        env_vars = setup_environment()
        
        # Initialize database (non-blocking, runs in background)
        # Don't wait too long for this - it can happen while app starts
        import threading
        db_thread = threading.Thread(target=initialize_database, daemon=True)
        db_thread.start()
        
        # Give database init a head start
        time.sleep(2)
        
        # Start API
        start_api(int(env_vars['PORT']))
        
    except Exception as e:
        print(f"❌ Fatal error during startup: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check deployment logs")
        print("2. Ensure DATABASE_URL is set if using PostgreSQL")
        print("3. Check requirements.txt for compatibility")
        print("4. Try running minimal test: python test_minimal.py")
        
        # Try to start minimal API as fallback
        print("\n🔄 Attempting to start minimal API as fallback...")
        time.sleep(2)
        port = int(os.environ.get('PORT', 8000))
        os.execvp('uvicorn', ['uvicorn', 'test_minimal:app', '--host', '0.0.0.0', '--port', str(port)])

if __name__ == "__main__":
    main()