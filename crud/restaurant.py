from sqlalchemy.orm import Session

from models.restaurant import Restaurant
from schemas.restaurant import RestaurantCreate

def get_restaurant(db: Session, restaurant_id: int):
     return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

def create_restaurant(db: Session, restaurant_create: RestaurantCreate):
     db_restaurant = Restaurant(
          name=restaurant_create.name,
          address=restaurant_create.address,
          phone=restaurant_create.phone,
          latitude=restaurant_create.latitude,
          longitude=restaurant_create.longitude
     )
     db.add(db_restaurant)
     db.commit()
     db.refresh(db_restaurant)
     return db_restaurant