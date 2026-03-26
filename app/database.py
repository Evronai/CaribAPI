from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import sys

# Log database connection (safe, hides credentials)
db_url = settings.database_url
if '@' in db_url:
    # Hide credentials: show only after @
    display_url = '...@' + db_url.split('@')[-1]
else:
    display_url = db_url
print(f"🔌 Connecting to database: {display_url}", file=sys.stderr)

# Create engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models here to ensure they're registered with Base
from app.models.user import User
from app.models.business import Business
from app.models.api_request import APIRequest

# Create tables
def create_tables():
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)