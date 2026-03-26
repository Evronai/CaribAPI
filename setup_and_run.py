#!/usr/bin/env python3
"""
Railway deployment setup script
Sets up database, creates sample data, and starts the API
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Set up environment variables for Railway"""
    print("🚀 Setting up CaribAPI on Railway...")
    
    # Get Railway environment variables
    env_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'REDIS_URL': os.environ.get('REDIS_URL'),
        'PORT': os.environ.get('PORT', '8000'),
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
    }
    
    print(f"Environment: {env_vars['RAILWAY_ENVIRONMENT']}")
    print(f"Port: {env_vars['PORT']}")
    print(f"Database URL: {'Set' if env_vars['DATABASE_URL'] else 'Not set'}")
    print(f"Redis URL: {'Set' if env_vars['REDIS_URL'] else 'Not set'}")
    
    # Create .env file for the application
    env_content = f"""# Railway Production Environment
API_TITLE=CaribAPI
API_VERSION=1.0.0
API_DESCRIPTION=Caribbean Business Data API
CONTACT_EMAIL=contact@caribapi.com

# Database
DATABASE_URL={env_vars['DATABASE_URL'] or 'sqlite:///./caribapi.db'}

# Redis (optional)
REDIS_URL={env_vars['REDIS_URL'] or ''}

# JWT
SECRET_KEY={os.environ.get('SECRET_KEY', 'railway-production-secret-key-change-me')}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=*

# Rate Limiting
RATE_LIMIT_FREE=100
RATE_LIMIT_PRO=10000
RATE_LIMIT_BUSINESS=100000

# Stripe (set these in Railway dashboard)
STRIPE_SECRET_KEY={os.environ.get('STRIPE_SECRET_KEY', '')}
STRIPE_WEBHOOK_SECRET={os.environ.get('STRIPE_WEBHOOK_SECRET', '')}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    
    return env_vars

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print(f"⚠️  Dependency installation had issues: {result.stderr[:200]}")
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")
        # Continue anyway - Railway might have already installed them

def setup_database():
    """Set up database and create sample data"""
    print("\n🗃️  Setting up database...")
    
    try:
        # First, check if we can import the database module
        sys.path.append('.')
        
        # Try to create tables and sample data
        result = subprocess.run(
            [sys.executable, 'scripts/create_sample_data.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database setup completed")
            print(result.stdout[-500:])  # Last 500 chars of output
        else:
            print(f"⚠️  Database setup had issues: {result.stderr[:500]}")
            print("Will start API anyway - database might be read-only")
            
    except Exception as e:
        print(f"❌ Database setup error: {str(e)}")
        print("Will start API with minimal functionality")

def start_api(port):
    """Start the FastAPI application"""
    print(f"\n🚀 Starting CaribAPI on port {port}...")
    print("=" * 60)
    print("📡 API will be available at: https://your-project.railway.app")
    print("📚 Documentation: https://your-project.railway.app/docs")
    print("🔑 Test API Key: test_api_key_1234567890")
    print("=" * 60)
    
    # Use uvicorn to start the app
    # First check if we're using the full app or minimal test
    if os.path.exists('app/main.py'):
        # Use the full application
        import_command = 'app.main:app'
    else:
        # Use the minimal test app
        import_command = 'test_minimal:app'
        print("⚠️  Using minimal test API (full app not found)")
        print("   Deploy from GitHub for full functionality")
    
    # Start the server
    os.execvp('uvicorn', [
        'uvicorn', import_command,
        '--host', '0.0.0.0',
        '--port', port,
        '--reload' if os.environ.get('RAILWAY_ENVIRONMENT') == 'development' else ''
    ])

def main():
    """Main setup function"""
    try:
        # Setup
        env_vars = setup_environment()
        
        # Install dependencies
        install_dependencies()
        
        # Setup database (if possible)
        setup_database()
        
        # Start API
        start_api(env_vars['PORT'])
        
    except Exception as e:
        print(f"❌ Fatal error during setup: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check Railway logs for more details")
        print("2. Ensure DATABASE_URL is set in Railway variables")
        print("3. Check requirements.txt for compatibility")
        print("4. Try deploying from GitHub instead of local files")
        
        # Try to start minimal API anyway
        print("\n🔄 Attempting to start minimal API...")
        time.sleep(2)
        start_api(os.environ.get('PORT', '8000'))

if __name__ == "__main__":
    main()