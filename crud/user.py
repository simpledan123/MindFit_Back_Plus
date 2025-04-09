from sqlalchemy.orm import Session
from core.security import hash_password
from models.user import User
from schemas.user import UserCreate


def create_user(db: Session, user_create: UserCreate) -> User:
    db_user = User(
        email=user_create.email,
        nickname=user_create.nickname,
        hashed_password=hash_password(user_create.password1)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()