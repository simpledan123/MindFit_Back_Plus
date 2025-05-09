# MindFit_Back_Plus-main/schemas/bookmark.py
from pydantic import BaseModel
from typing import List
from .restaurant import RestaurantRead # 북마크된 식당 정보를 포함하기 위함 (상대 경로 사용)

# BookmarkCreate는 API 경로에서 restaurant_id를 직접 받으므로 별도로 필요하지 않을 수 있습니다.

# 북마크된 식당 정보를 반환하기 위한 스키마 (RestaurantRead를 그대로 사용하거나 확장)
class BookmarkRead(RestaurantRead):
    # RestaurantRead의 모든 필드를 상속받음
    pass

    class Config:
        from_attributes = True
