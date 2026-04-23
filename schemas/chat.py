from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    message: str


class RestaurantLocation(BaseModel):
    """챗봇 추천 결과로 지도에 표시될 식당 위치 정보"""
    id: Optional[int] = None
    name: str
    address: str
    latitude: float
    longitude: float
    rating: float = 0.0


class ChatResponse(BaseModel):
    response: str
    restaurants: List[RestaurantLocation] = []
