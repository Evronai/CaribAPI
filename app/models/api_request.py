from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class APIRequest(BaseModel):
    __tablename__ = "api_requests"
    
    # Request info
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)  # GET, POST, etc.
    
    # Parameters
    query_params = Column(Text)  # JSON string of query parameters
    request_body = Column(Text)  # JSON string of request body
    
    # Response
    status_code = Column(Integer)
    response_time_ms = Column(Integer)  # Response time in milliseconds
    
    # IP and location
    ip_address = Column(String)
    user_agent = Column(Text)
    
    # Cost tracking (for billing)
    cost_units = Column(Integer, default=1)  # How many "units" this request cost
    
    # Relationships
    user = relationship("User", back_populates="api_requests")
    
    def __repr__(self):
        return f"<APIRequest {self.endpoint} by user {self.user_id} at {self.created_at}>"