# MindFit_Back_Plus-main/crud/bookmark.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from models.restaurant import Restaurant

def create_bookmark(db: Session, user: User, restaurant_id: int) -> Restaurant:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    if restaurant in user.bookmarked_restaurants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant already bookmarked")

    user.bookmarked_restaurants.append(restaurant)
    db.commit()
    return restaurant

def get_user_bookmarks(db: Session, user: User) -> list[Restaurant]:
    return user.bookmarked_restaurants

def delete_bookmark(db: Session, user: User, restaurant_id: int) -> None:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    if restaurant not in user.bookmarked_restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found for this restaurant")

    user.bookmarked_restaurants.remove(restaurant)
    db.commit()
    return
