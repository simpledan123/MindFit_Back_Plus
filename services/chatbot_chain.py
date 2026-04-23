"""
LangGraph 기반 맛집 추천 멀티스텝 에이전트
- 의도 분류 → 조건부 라우팅 → RAG 검색 → 응답 생성
- API 응답에 식당 위치 정보(위도/경도)를 포함하여 프론트 지도 연동 지원
"""

from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document, SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
import sqlite3

from crud.chatbot import get_user_summary, save_user_summary, save_user_keywords, get_user_keywords
from models.user import User
from sqlalchemy.orm import Session

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    model_name="gpt-4o-mini",
    temperature=0
)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)


# ── 벡터스토어 초기화 ──
def init_vectorstore():
    conn = sqlite3.connect("prac.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, address, phone, rating, latitude, longitude
        FROM restaurants
    """)
    rows = cursor.fetchall()
    conn.close()

    documents = []
    for row in rows:
        id_, name, address, phone, rating, lat, lng = row
        content = f"""식당명: {name}
주소: {address}
전화번호: {phone or '정보없음'}
평점: {rating}
위도: {lat}
경도: {lng}"""
        documents.append(Document(
            page_content=content,
            metadata={
                "id": id_, "name": name, "address": address,
                "latitude": lat, "longitude": lng, "rating": rating
            }
        ))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)
    return FAISS.from_documents(docs, embeddings)


vectorstore = init_vectorstore()


# ── State 정의 ──
class ChatState(TypedDict):
    user_id: int
    message: str
    db: Session
    intent: str
    summary: str
    keywords: List[str]
    location_filter: Optional[str]
    search_results: List[Document]
    response: str


# ── 노드 함수 ──

def load_user_context(state: ChatState) -> ChatState:
    db = state["db"]
    user_id = state["user_id"]

    summary_obj = get_user_summary(db, user_id)
    summary = getattr(summary_obj, "summary", "") or ""
    lines = summary.strip().split("\n")
    if len(lines) > 10:
        summary = "\n".join(lines[-10:])

    keywords_obj = get_user_keywords(db, user_id)
    keywords = []
    if keywords_obj and hasattr(keywords_obj, '__iter__'):
        keywords = [kw.keyword for kw in keywords_obj]

    return {**state, "summary": summary, "keywords": keywords}


def classify_intent(state: ChatState) -> ChatState:
    message = state["message"]
    summary = state["summary"]

    preference_ask_patterns = ["좋아하는 음식", "내가 뭘 좋아", "취향", "선호"]
    if any(p in message for p in preference_ask_patterns):
        return {**state, "intent": "선호도_질문"}

    preference_save_patterns = ["좋아해", "싫어해", "못 먹어", "알러지", "선호해"]
    if any(p in message for p in preference_save_patterns):
        return {**state, "intent": "선호도_저장"}

    system_prompt = """사용자의 메시지가 맛집/식당 추천 요청인지, 일반 대화인지 판단하세요.
반드시 "추천" 또는 "대화" 중 하나만 출력하세요."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"사용자 메시지: {message}\n이전 대화 요약: {summary[:200] if summary else '없음'}")
    ]
    result = llm.invoke(messages).content.strip()
    intent = "추천" if "추천" in result else "대화"
    return {**state, "intent": intent}


def extract_location(state: ChatState) -> ChatState:
    message = state["message"]
    location_keywords = ["근처", "주변", "강남", "홍대", "이태원", "신촌", "명동", "종로"]
    location_filter = next((loc for loc in location_keywords if loc in message), None)
    return {**state, "location_filter": location_filter}


def rag_search(state: ChatState) -> ChatState:
    message = state["message"]
    keywords = state["keywords"]
    location_filter = state.get("location_filter")

    search_query = message
    if keywords:
        search_query += " " + " ".join(keywords[:3])

    results = vectorstore.similarity_search(search_query, k=5)

    if location_filter and location_filter not in ["근처", "주변"]:
        filtered = [
            doc for doc in results
            if location_filter in doc.metadata.get("address", "")
        ]
        results = filtered if filtered else results[:3]

    results = sorted(results, key=lambda x: x.metadata.get("rating", 0), reverse=True)[:3]
    return {**state, "search_results": results}


def generate_recommendation(state: ChatState) -> ChatState:
    message = state["message"]
    search_results = state["search_results"]
    keywords = state["keywords"]

    if not search_results:
        return {**state, "response": "죄송해요, 조건에 맞는 식당을 찾지 못했어요. 다른 조건으로 다시 말씀해 주세요!"}

    restaurant_info = "\n\n".join([
        f"[{i+1}] {doc.metadata['name']}\n   주소: {doc.metadata['address']}\n   평점: {doc.metadata['rating']}"
        for i, doc in enumerate(search_results)
    ])

    system_prompt = """당신은 친근한 맛집 추천 챗봇입니다.
검색된 식당 정보를 바탕으로 사용자에게 자연스럽게 추천해주세요.
이모지를 적절히 사용하고, 각 식당의 특징을 간단히 설명해주세요."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"사용자 요청: {message}\n선호 키워드: {', '.join(keywords) if keywords else '없음'}\n\n{restaurant_info}\n\n위 정보를 바탕으로 추천해주세요."),
    ]
    response = llm.invoke(messages).content.strip()
    return {**state, "response": response}


def generate_conversation(state: ChatState) -> ChatState:
    message = state["message"]
    summary = state["summary"]

    system_prompt = """당신은 친근한 맛집 추천 챗봇입니다.
사용자와 자연스럽게 대화하되, 음식 관련 대화로 유도해주세요."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"이전 대화 요약: {summary[:300] if summary else '없음'}\n\n사용자: {message}")
    ]
    response = llm.invoke(messages).content.strip()
    return {**state, "response": response}


def handle_preference_question(state: ChatState) -> ChatState:
    keywords = state["keywords"]
    if keywords:
        response = f"지금까지 대화를 보면, {', '.join(keywords)} 같은 음식을 좋아하시는 것 같아요! 😋"
    else:
        response = "아직 취향을 잘 모르겠어요! 좋아하는 음식 종류를 알려주시면 더 잘 추천해드릴 수 있어요. 🤔"
    return {**state, "response": response}


def handle_preference_save(state: ChatState) -> ChatState:
    message = state["message"]
    system_prompt = """사용자 메시지에서 음식 선호도 키워드를 추출하세요. 쉼표로 구분된 키워드만 출력하세요."""
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=message)]
    extracted = llm.invoke(messages).content.strip()
    new_keywords = [kw.strip() for kw in extracted.split(",") if kw.strip()]
    response = f"알겠어요! '{', '.join(new_keywords)}' 취향을 기억할게요! 📝"
    return {**state, "response": response, "keywords": list(set(state["keywords"] + new_keywords))}


def save_context(state: ChatState) -> ChatState:
    db = state["db"]
    user_id = state["user_id"]
    summary = state["summary"]
    keywords = state["keywords"]

    new_summary = f"{summary}\n[User]: {state['message']}\n[Bot]: {state['response'][:100]}..."
    lines = new_summary.strip().split("\n")
    if len(lines) > 10:
        new_summary = "\n".join(lines[-10:])

    save_user_summary(db, user_id, new_summary)

    if state["intent"] == "추천" and keywords:
        save_user_keywords(db, user_id, keywords)

    return state


# ── 라우팅 ──
def route_by_intent(state: ChatState) -> str:
    intent = state["intent"]
    if intent == "추천":
        return "extract_location"
    elif intent == "선호도_질문":
        return "handle_preference_question"
    elif intent == "선호도_저장":
        return "handle_preference_save"
    else:
        return "generate_conversation"


# ── 그래프 구성 ──
def build_chatbot_graph():
    workflow = StateGraph(ChatState)

    workflow.add_node("load_user_context", load_user_context)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("extract_location", extract_location)
    workflow.add_node("rag_search", rag_search)
    workflow.add_node("generate_recommendation", generate_recommendation)
    workflow.add_node("generate_conversation", generate_conversation)
    workflow.add_node("handle_preference_question", handle_preference_question)
    workflow.add_node("handle_preference_save", handle_preference_save)
    workflow.add_node("save_context", save_context)

    workflow.set_entry_point("load_user_context")
    workflow.add_edge("load_user_context", "classify_intent")

    workflow.add_conditional_edges("classify_intent", route_by_intent, {
        "extract_location": "extract_location",
        "handle_preference_question": "handle_preference_question",
        "handle_preference_save": "handle_preference_save",
        "generate_conversation": "generate_conversation",
    })

    workflow.add_edge("extract_location", "rag_search")
    workflow.add_edge("rag_search", "generate_recommendation")
    workflow.add_edge("generate_recommendation", "save_context")
    workflow.add_edge("generate_conversation", "save_context")
    workflow.add_edge("handle_preference_question", "save_context")
    workflow.add_edge("handle_preference_save", "save_context")
    workflow.add_edge("save_context", END)

    return workflow.compile()


chatbot_graph = build_chatbot_graph()


# ── API 엔드포인트용 함수 ──
def generate_chat_response(user: User, message: str, db: Session) -> dict:
    """
    FastAPI 엔드포인트에서 호출하는 메인 함수.
    response(str) + restaurants(List) 를 반환하여 프론트 지도 연동 지원.
    """
    initial_state: ChatState = {
        "user_id": user.id,
        "message": message,
        "db": db,
        "intent": "",
        "summary": "",
        "keywords": [],
        "location_filter": None,
        "search_results": [],
        "response": "",
    }

    result = chatbot_graph.invoke(initial_state)

    # 추천 결과가 있을 때 식당 위치 정보 추출
    restaurants = []
    if result.get("intent") == "추천" and result.get("search_results"):
        for doc in result["search_results"]:
            m = doc.metadata
            if m.get("latitude") and m.get("longitude"):
                restaurants.append({
                    "id": m.get("id"),
                    "name": m.get("name", ""),
                    "address": m.get("address", ""),
                    "latitude": float(m["latitude"]),
                    "longitude": float(m["longitude"]),
                    "rating": float(m.get("rating", 0)),
                })

    return {"response": result["response"], "restaurants": restaurants}
