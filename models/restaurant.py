# MindFit_Back_Plus-main/models/restaurant.py
from sqlalchemy import Column, Integer, String, Float, DECIMAL
from sqlalchemy.orm import relationship
from db.database import Base
from .bookmark import user_restaurant_bookmark_association # 상대 경로 사용

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    rating = Column(Float, nullable=False, default=0.0)
    kakao_rating = Column(Float, nullable=True)
    address = Column(String, nullable=False)
    phone = Column(String(20))
    opening_hours = Column(String)
    latitude = Column(DECIMAL(10, 7), nullable=True)
    longitude = Column(DECIMAL(10, 7), nullable=True)
    place_id = Column(String, unique=True)

    # 기존 관계 수정 및 명시 (back_populates 사용 권장)
    reviews = relationship("Review", back_populates="restaurant", cascade="all, delete-orphan")
    menus = relationship("Menu", back_populates="restaurant", cascade="all, delete-orphan")

    # Restaurant와 User 간의 다대다 관계 설정 (북마크)
    bookmarked_by_users = relationship(
        "User", # 문자열로 모델 이름 지정
        secondary=user_restaurant_bookmark_association,
        back_populates="bookmarked_restaurants"
    )
