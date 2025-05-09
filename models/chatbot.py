# MindFit_Back_Plus-main/models/chatbot.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class UserSummary(Base):
    __tablename__ = "user_summary"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    summary = Column(String)

    user = relationship("User", back_populates="summary")


class UserKeyword(Base):
    __tablename__ = "user_keywords"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    keyword = Column(String, primary_key=True)
    count = Column(Integer, default=1)

    user = relationship("User", back_populates="keywords")
