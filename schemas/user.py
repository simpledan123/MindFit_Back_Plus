from enum import Enum

from pydantic import BaseModel, model_validator, field_validator, EmailStr

from models.user import UserRole

class UserRead(BaseModel):
    id: int
    nickname: str
    role: UserRole

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

    @model_validator(mode="before")
    def validate_password_match(cls, values: dict) -> dict:
        if values.get("password1") != values.get("password2"):
            raise ValueError("패스워드가 맞지 않습니다.")
        return values
