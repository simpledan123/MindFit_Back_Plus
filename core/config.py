import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int (os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

settings = Settings()