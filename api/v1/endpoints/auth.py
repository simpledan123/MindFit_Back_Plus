from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.dependencies import get_db
from core.security import create_access_token, verify_password
from crud.user import get_user_by_email
from schemas.token import Token

router = APIRouter()

@router.post("/token", response_model=Token)
def login(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "nickname": user.nickname, "role": str(user.role)})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }