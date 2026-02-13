import os

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

url = make_url(SQLALCHEMY_DATABASE_URL)

connect_args = {}
engine_kwargs = {
    # 끊어진 커넥션을 풀에서 꺼냈을 때 자동으로 감지/교체 (운영형에 유리)
    "pool_pre_ping": True,
}

# SQLite 전용 옵션은 SQLite일 때만!
if url.drivername.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # MySQL/PostgreSQL 같은 운영형 DB는 커넥션 풀 옵션을 주는 게 자연스러움
    engine_kwargs.update(
        {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
        }
    )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
