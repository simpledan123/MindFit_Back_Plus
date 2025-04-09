from pydantic import BaseModel
from decimal import Decimal

from schemas.user import UserRead
from schemas.review import ReviewRead

class RestaurantRead(BaseModel):
    id: int
    name: str
    rating: float
    address: str
    phone: str
    latitude: Decimal
    longitude: Decimal
    reviews: list[ReviewRead] = []

class RestaurantCreate(BaseModel):
    name: str
    address: str
    phone: str
    latitude: Decimal
    longitude: Decimal
    




