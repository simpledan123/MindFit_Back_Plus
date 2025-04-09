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

    user = relationship("User", backref="reviews")
    restaurant = relationship("Restaurant", backref="reviews")