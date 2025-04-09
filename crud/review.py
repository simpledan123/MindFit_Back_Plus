from sqlalchemy.orm import Session
from models.user import User
from models.review import Review
from schemas.review import ReviewCreate

def create_review(db: Session, user: User, restaurant_id: int, review_create: ReviewCreate):
    db_review = Review(
        rating=review_create.rating,
        comment=review_create.comment,
        user_id=user.id,
        restaurant_id=restaurant_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review