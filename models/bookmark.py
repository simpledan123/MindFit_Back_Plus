# MindFit_Back_Plus-main/models/bookmark.py
from sqlalchemy import Table, Column, Integer, ForeignKey
from db.database import Base

# 사용자-식당 북마크 연결 테이블 (다대다 관계)
user_restaurant_bookmark_association = Table(
    'user_restaurant_bookmarks', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('restaurant_id', Integer, ForeignKey('restaurants.id', ondelete="CASCADE"), primary_key=True)
)
