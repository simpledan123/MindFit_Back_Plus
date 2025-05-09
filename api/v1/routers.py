# MindFit_Back_Plus-main/api/v1/routers.py
from fastapi import APIRouter
from api.v1.endpoints import chatbot, auth, restaurants, reviews, users, bookmarks # bookmarks 추가

api_router = APIRouter()

# 각 기능별 라우터 등록 (태그 이름은 원하는 대로 변경 가능)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"]) # 북마크 라우터 등록
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
