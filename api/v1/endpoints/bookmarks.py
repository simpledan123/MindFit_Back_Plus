# MindFit_Back_Plus-main/api/v1/endpoints/bookmarks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user
from models.user import User
# BookmarkRead 스키마를 사용해도 되고, RestaurantRead를 직접 사용해도 됩니다.
# CRUD 함수가 Restaurant 객체를 반환하므로 RestaurantRead가 더 직관적일 수 있습니다.
from schemas.restaurant import RestaurantRead
import crud.bookmark

router = APIRouter()

@router.post(
    "/restaurants/{restaurant_id}",
    response_model=RestaurantRead,
    status_code=status.HTTP_201_CREATED,
    summary="식당 북마크 추가",
    description="현재 로그인한 사용자의 북마크에 특정 식당을 추가합니다."
)
def add_restaurant_to_bookmarks(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmarked_restaurant = crud.bookmark.create_bookmark(db=db, user=current_user, restaurant_id=restaurant_id)
    return bookmarked_restaurant

@router.get(
    "/",
    response_model=List[RestaurantRead],
    summary="사용자 북마크 목록 조회",
    description="현재 로그인한 사용자의 모든 북마크된 식당 정보를 조회합니다."
)
def read_user_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmarks = crud.bookmark.get_user_bookmarks(db=db, user=current_user)
    return bookmarks

@router.delete(
    "/restaurants/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="식당 북마크 삭제",
    description="현재 로그인한 사용자의 북마크에서 특정 식당을 삭제합니다."
)
def remove_restaurant_from_bookmarks(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crud.bookmark.delete_bookmark(db=db, user=current_user, restaurant_id=restaurant_id)
    return
