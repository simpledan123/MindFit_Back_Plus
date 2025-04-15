from pydantic import BaseModel
from schemas.user import UserRead
from typing import Optional


class ReviewRead(BaseModel):
    id: int
    rating: float
    comment: str
    user: Optional[UserRead]


class ReviewCreate(BaseModel):
    rating: float
    comment: str
