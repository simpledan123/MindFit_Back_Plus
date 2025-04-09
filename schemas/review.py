from pydantic import BaseModel

from schemas.user import UserRead

class ReviewRead(BaseModel):
    id: int
    rating: float
    comment: str
    user: UserRead | None

class ReviewCreate(BaseModel):
    rating: float
    comment: str