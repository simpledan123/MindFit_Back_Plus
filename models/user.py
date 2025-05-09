# MindFit_Back_Plus-main/models/user.py
from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from db.database import Base
# models.bookmark 대신 .bookmark로 상대 경로 사용 가능 (models 패키지 내이므로)
# 또는 models.__init__.py에서 import 했다면 from . import user_restaurant_bookmark_association 가능
from .bookmark import user_restaurant_bookmark_association

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)

    # User와 Restaurant 간의 다대다 관계 설정 (북마크)
    bookmarked_restaurants = relationship(
        "Restaurant", # 문자열로 모델 이름 지정
        secondary=user_restaurant_bookmark_association,
        back_populates="bookmarked_by_users"
    )

    # 기존 관계 수정 및 명시 (back_populates 사용 권장)
    summary = relationship("UserSummary", back_populates="user", uselist=False, cascade="all, delete-orphan")
    keywords = relationship("UserKeyword", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")
