# MindFit_Back_Plus-main/models/__init__.py
from db.database import Base # Base를 여기서 한번 import 해두면 env.py에서 참조하기 용이

from .user import User, UserRole
from .restaurant import Restaurant
from .review import Review
from .menu import Menu
from .keyword import Keyword, menu_keywords
from .chatbot import UserSummary, UserKeyword
from .bookmark import user_restaurant_bookmark_association

# 이 파일이 있으면, 다른 곳에서 from models import User 처럼 사용 가능
