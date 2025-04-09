from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_admin_user
from models.user import User
from schemas.restaurant import RestaurantRead, RestaurantCreate
import crud.restaurant

router = APIRouter()

@router.get("/{restaurant_id}", response_model=RestaurantRead)
def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    current_restaurant = crud.restaurant.get_restaurant(db, restaurant_id)
    return current_restaurant

@router.post("/", response_model=RestaurantRead)
def create_restaurant(restaurant_create: RestaurantCreate,
                    db: Session = Depends(get_db), 
                    admin_user: User = Depends(get_admin_user)):
    return crud.restaurant.create_restaurant(db, restaurant_create)

