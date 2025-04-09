from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.user import User
from schemas.user import UserCreate, UserRead
import crud.user

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

@router.post("/", response_model=UserRead, status_code=201)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    return crud.user.create_user(db, user_create)