from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    nko_name = Column(String(100), nullable=False)
    nko_activity = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)