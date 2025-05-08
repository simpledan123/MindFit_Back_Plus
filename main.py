from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas.chat import ChatRequest
from api.v1.routers import api_router

from chat_chain_v2 import generate_chat_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
