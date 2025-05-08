from fastapi import APIRouter
from api.v1.endpoints import chatbot, auth, restaurants, reviews, users

api_router = APIRouter()

# 각 기능별 라우터 등록
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
