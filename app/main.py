from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
import logging

from app.config import settings
from app.database import create_tables, get_db
from app.auth import get_current_user, increment_request_count, check_rate_limit
from app.models.user import User
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting CaribAPI...")
    create_tables()
    logger.info("Database tables created/verified")
    
    # Create sample data if needed
    # await create_sample_data()
    
    yield
    
    # Shutdown
    logger.info("Shutting down CaribAPI...")

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    contact={"email": settings.contact_email},
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for certain paths
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        return await call_next(request)
    
    # Get user from API key
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        # Try to get from query params (for testing)
        api_key = request.query_params.get("api_key")
    
    if api_key:
        db = next(get_db())
        try:
            user = db.query(User).filter(User.api_key == api_key).first()
            if user:
                # Check rate limit
                if not check_rate_limit(user, db):
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"You have exceeded your daily limit of {user.daily_limit} requests. Upgrade your plan for higher limits."
                        }
                    )
        finally:
            db.close()
    
    response = await call_next(request)
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = (time.time() - start_time) * 1000
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.2f}ms"
    )
    
    # Add header with processing time
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CaribAPI",
        "version": settings.api_version,
        "timestamp": time.time()
    }

# API info endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to CaribAPI - Caribbean Business Data Platform",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "businesses": "/api/v1/businesses",
            "search": "/api/v1/businesses/search",
            "by_id": "/api/v1/businesses/{id}",
            "auth": {
                "register": "/api/v1/auth/register",
                "login": "/api/v1/auth/login",
                "profile": "/api/v1/auth/me"
            }
        }
    }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Your API key for authentication"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for authentication"
        }
    }
    
    # Add global security
    openapi_schema["security"] = [{"APIKeyHeader": []}, {"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Import routers
from app.routers import auth, businesses

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(businesses.router, prefix="/api/v1/businesses", tags=["Businesses"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)