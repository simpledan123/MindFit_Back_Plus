# MindFit_Back_Plus-main/schemas/user.py
from enum import Enum
from pydantic import BaseModel, model_validator, EmailStr
from models.user import UserRole # models 패키지 내 User 모델에서 직접 가져오기
from typing import List, Optional # Optional 추가
from .bookmark import BookmarkRead # 상대 경로 사용
from .review import ReviewRead # UserRead에 리뷰 목록을 포함시키려면 추가

class UserRead(BaseModel):
    id: int
    nickname: str
    role: UserRole
    bookmarked_restaurants: List[BookmarkRead] = []
    # reviews: List[ReviewRead] = [] # 사용자가 작성한 리뷰 목록을 포함하고 싶다면 추가

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    nickname: str
    password1: str
    password2: str

    @model_validator(mode="before")
    def validate_not_empty(cls, values: dict) -> dict:
        for field, value in values.items():
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"'{field}' 필드는 빈 문자열이 될 수 없습니다.")
        return values

    @model_validator(mode="after") # password1, password2가 모두 들어온 후 비교
    def validate_password_match(cls, values: dict) -> dict:
        pw1 = values.get("password1")
        pw2 = values.get("password2")
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("패스워드가 맞지 않습니다.")
        return values
