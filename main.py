from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from api.v1.routers import api_router

app = FastAPI()


app.include_router(api_router, prefix="/api/v1")

'''
$env:PYTHONPATH="." ; python crawling/data_crawling.py
명령어 실행을 통해 데이터 크롤링!
'''