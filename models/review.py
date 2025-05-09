# MindFit_Back_Plus-main/models/review.py
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from db.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float, nullable=False, default=0.0)
    comment = Column(String, nullable=False)

    user = relationship("User", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")
