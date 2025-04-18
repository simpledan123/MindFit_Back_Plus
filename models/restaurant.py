from sqlalchemy import Column, Integer, String, Float, DECIMAL
from sqlalchemy.orm import relationship
from db.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    rating = Column(Float, nullable=False, default=0.0)  # Google 평점
    kakao_rating = Column(Float, nullable=True)  # ← 여기 추가됨!
    address = Column(String, nullable=False)
    phone = Column(String(20))
    opening_hours = Column(String)
    latitude = Column(DECIMAL(10, 7), nullable=True)
    longitude = Column(DECIMAL(10, 7), nullable=True)
    place_id = Column(String, unique=True)

