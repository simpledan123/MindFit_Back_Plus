import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # DB는 기본값 제공 (기존 동작 유지)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./prac.db")

    # 나머지는 기존대로 환경변수 기반 (없으면 None일 수 있음)
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))


settings = Settings()
