# MindFit_Back_Plus-main/models/menu.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    menu_item = Column(String, nullable=False)
    price = Column(String)

    restaurant = relationship("Restaurant", back_populates="menus")
