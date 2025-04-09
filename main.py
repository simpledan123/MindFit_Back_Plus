from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from api.v1.routers import api_router

app = FastAPI()


app.include_router(api_router, prefix="/api/v1")

'''
실행 전에, 최상위경로에 .env파일을 만들어야 함 (내용은 README 찹조)
.env파일과 data_crawling.py 파일과 chat_chain_v2.py에 API 키 필요
'''

#설정 끝났으면 터미널에서 아래 명령어 차례대로 실행

'''
alembic revision --autogenerate -m
마이그레이션 파일 생성
alembic upgrade head
db 업데이트
'''

'''
python crawling/data_crawling.py
데이터 크롤링 (아마 이미 되어있을것임)
'''

'''
python chat_chain_v2.py
챗봇 실행
'''