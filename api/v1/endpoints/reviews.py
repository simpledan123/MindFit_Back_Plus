from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.user import User
from models.review import Review
from schemas.review import ReviewRead, ReviewCreate
import crud.review

router = APIRouter()

@router.post("/restaurant_id={restaurant_id}", response_model=ReviewRead)
def create_review(restaurant_id: int, review_create: ReviewCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.review.create_review(db, user, restaurant_id, review_create) 