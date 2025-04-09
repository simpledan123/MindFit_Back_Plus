from sqlalchemy import Column, Integer, String, Float, DECIMAL
from sqlalchemy.orm import relationship
from db.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    rating = Column(Float, nullable=False, default=0.0)
    address = Column(String, nullable=False)
    phone = Column(String(20))
    opening_hours = Column(String)
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    place_id = Column(String, unique=True) 