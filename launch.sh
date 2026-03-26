#!/bin/bash

# CaribAPI Launch Script
# This script sets up and launches the CaribAPI service

set -e

echo "🚀 Launching CaribAPI - Caribbean Business Data Platform"
echo "========================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

# Check if PostgreSQL is running (optional)
if command -v pg_isready &> /dev/null; then
    if ! pg_isready -q; then
        echo "⚠️  PostgreSQL is not running. Starting with Docker Compose..."
        USE_DOCKER=true
    else
        echo "✓ PostgreSQL is running"
        USE_DOCKER=false
    fi
else
    echo "⚠️  PostgreSQL not found. Starting with Docker Compose..."
    USE_DOCKER=true
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
    echo "   - Set DATABASE_URL to your PostgreSQL connection"
    echo "   - Set STRIPE_SECRET_KEY for payment processing"
    echo "   - Set SECRET_KEY for JWT tokens"
    read -p "Press Enter to continue with default values..."
fi

# Start services
if [ "$USE_DOCKER" = true ]; then
    echo "Starting services with Docker Compose..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    # Start services
    docker-compose up -d
    
    echo "Waiting for services to start..."
    sleep 10
    
    # Create sample data
    echo "Creating sample data..."
    docker-compose exec api python scripts/create_sample_data.py
    
else
    # Create sample data directly
    echo "Creating sample data..."
    python scripts/create_sample_data.py
fi

# Start the API server
echo "Starting CaribAPI server..."
echo "📡 API will be available at: http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "🔑 Test API Key: test_api_key_1234567890"
echo ""
echo "💡 For production deployment, consider:"
echo "   - Render: See RENDER_DEPLOYMENT.md (free tier)"
echo "   - Railway: See RAILWAY_DEPLOYMENT.md (free tier)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload