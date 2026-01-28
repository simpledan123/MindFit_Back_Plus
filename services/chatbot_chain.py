"""
LangGraph 기반 맛집 추천 멀티스텝 에이전트
- 의도 분류 → 조건부 라우팅 → RAG 검색 → 응답 생성
- JD 매칭: LangChain/LangGraph 기반 멀티스텝 에이전트, 프롬프트 체이닝, 라우팅
"""

from typing import TypedDict, Literal, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document, SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
import sqlite3
import operator

from crud.chatbot import get_user_summary, save_user_summary, save_user_keywords, get_user_keywords
from models.user import User
from sqlalchemy.orm import Session

# 환경 변수 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# LLM 설정
llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    model_name="gpt-4o-mini",
    temperature=0
)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)


# ============================================
# 벡터스토어 초기화 (식당 데이터 로딩)
# ============================================
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
                "id": id_,
                "name": name,
                "address": address,
                "latitude": lat,
                "longitude": lng,
                "rating": rating
            }
        ))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)
    return FAISS.from_documents(docs, embeddings)


vectorstore = init_vectorstore()


# ============================================
# 상태 정의 (State Schema)
# ============================================
class ChatState(TypedDict):
    # 입력
    user_id: int
    message: str
    db: Session
    
    # 중간 처리
    intent: str  # "추천" | "대화" | "선호도_질문" | "선호도_저장"
    summary: str
    keywords: List[str]
    location_filter: Optional[str]
    
    # RAG 결과
    search_results: List[Document]
    
    # 출력
    response: str


# ============================================
# 노드 함수들
# ============================================

def load_user_context(state: ChatState) -> ChatState:
    """사용자 컨텍스트 로드 (요약, 키워드)"""
    db = state["db"]
    user_id = state["user_id"]
    
    summary_obj = get_user_summary(db, user_id)
    summary = getattr(summary_obj, "summary", "") or ""
    
    # 요약 길이 제한 (최근 10줄만 유지)
    lines = summary.strip().split("\n")
    if len(lines) > 10:
        summary = "\n".join(lines[-10:])
    
    keywords_obj = get_user_keywords(db, user_id)
    keywords = []
    if keywords_obj:
        keywords = [kw.keyword for kw in keywords_obj] if hasattr(keywords_obj, '__iter__') else []
    
    return {
        **state,
        "summary": summary,
        "keywords": keywords
    }


def classify_intent(state: ChatState) -> ChatState:
    """의도 분류 노드 - 4가지 의도로 분류"""
    message = state["message"]
    summary = state["summary"]
    
    # 선호도 질문 패턴 체크
    preference_ask_patterns = ["좋아하는 음식", "내가 뭘 좋아", "취향", "선호"]
    if any(p in message for p in preference_ask_patterns):
        return {**state, "intent": "선호도_질문"}
    
    # 선호도 저장 패턴 체크
    preference_save_patterns = ["좋아해", "싫어해", "못 먹어", "알러지", "선호해"]
    if any(p in message for p in preference_save_patterns):
        return {**state, "intent": "선호도_저장"}
    
    # LLM으로 추천/대화 의도 분류
    system_prompt = """당신은 사용자 의도를 분류하는 분류기입니다.
사용자의 메시지가 다음 중 어느 의도인지 판단하세요:

1. "추천" - 맛집/식당/음식 추천을 원하는 경우
   예: "맛집 추천해줘", "뭐 먹을까", "근처 식당 알려줘", "점심 뭐 먹지"
   
2. "대화" - 일반적인 대화, 인사, 질문 등
   예: "안녕", "고마워", "오늘 날씨 어때", "심심해"

반드시 "추천" 또는 "대화" 중 하나만 출력하세요."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"사용자 메시지: {message}\n\n이전 대화 요약: {summary[:200] if summary else '없음'}")
    ]
    
    result = llm.invoke(messages).content.strip()
    intent = "추천" if "추천" in result else "대화"
    
    return {**state, "intent": intent}


def extract_location(state: ChatState) -> ChatState:
    """위치 정보 추출 노드"""
    message = state["message"]
    
    # 위치 키워드 추출
    location_keywords = ["근처", "주변", "강남", "홍대", "이태원", "신촌", "명동", "종로"]
    location_filter = None
    
    for loc in location_keywords:
        if loc in message:
            location_filter = loc
            break
    
    return {**state, "location_filter": location_filter}


def rag_search(state: ChatState) -> ChatState:
    """RAG 검색 노드 - 벡터 유사도 검색"""
    message = state["message"]
    keywords = state["keywords"]
    location_filter = state.get("location_filter")
    
    # 검색 쿼리 구성 (사용자 메시지 + 선호 키워드)
    search_query = message
    if keywords:
        search_query += " " + " ".join(keywords[:3])
    
    # 벡터 검색 (상위 5개)
    results = vectorstore.similarity_search(search_query, k=5)
    
    # 위치 필터링 (있는 경우)
    if location_filter and location_filter not in ["근처", "주변"]:
        results = [
            doc for doc in results 
            if location_filter in doc.metadata.get("address", "")
        ] or results[:3]
    
    # 평점순 정렬
    results = sorted(
        results, 
        key=lambda x: x.metadata.get("rating", 0), 
        reverse=True
    )[:3]
    
    return {**state, "search_results": results}


def generate_recommendation(state: ChatState) -> ChatState:
    """추천 응답 생성 노드"""
    message = state["message"]
    search_results = state["search_results"]
    keywords = state["keywords"]
    
    if not search_results:
        return {
            **state, 
            "response": "죄송해요, 조건에 맞는 식당을 찾지 못했어요. 다른 조건으로 다시 말씀해 주세요!"
        }
    
    # 검색 결과 포맷팅
    restaurant_info = "\n\n".join([
        f"[{i+1}] {doc.metadata['name']}\n"
        f"   주소: {doc.metadata['address']}\n"
        f"   평점: {doc.metadata['rating']}"
        for i, doc in enumerate(search_results)
    ])
    
    system_prompt = """당신은 친근한 맛집 추천 챗봇입니다.
검색된 식당 정보를 바탕으로 사용자에게 자연스럽게 추천해주세요.
- 이모지를 적절히 사용해주세요
- 각 식당의 특징을 간단히 설명해주세요
- 사용자의 선호도가 있다면 그에 맞게 추천 이유를 설명해주세요"""

    user_content = f"""사용자 요청: {message}
사용자 선호 키워드: {', '.join(keywords) if keywords else '아직 파악된 선호도 없음'}

검색된 식당 정보:
{restaurant_info}

위 정보를 바탕으로 자연스럽게 추천해주세요."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ]
    
    response = llm.invoke(messages).content.strip()
    
    return {**state, "response": response}


def generate_conversation(state: ChatState) -> ChatState:
    """일반 대화 응답 생성 노드"""
    message = state["message"]
    summary = state["summary"]
    
    system_prompt = """당신은 친근한 맛집 추천 챗봇입니다.
사용자와 자연스럽게 대화하되, 음식이나 맛집 관련 대화로 유도해주세요.
- 친근하고 따뜻한 톤을 유지하세요
- 이모지를 적절히 사용하세요
- 대화가 길어지면 맛집 추천을 제안해주세요"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"이전 대화 요약: {summary[:300] if summary else '없음'}\n\n사용자: {message}")
    ]
    
    response = llm.invoke(messages).content.strip()
    
    return {**state, "response": response}


def handle_preference_question(state: ChatState) -> ChatState:
    """선호도 질문 처리 노드"""
    keywords = state["keywords"]
    
    if keywords:
        keyword_str = ", ".join(keywords)
        response = f"지금까지 대화를 보면, {keyword_str} 같은 음식을 좋아하시는 것 같아요! 😋\n혹시 더 알려주실 취향이 있으신가요?"
    else:
        response = "아직 취향을 잘 모르겠어요! 🤔\n좋아하는 음식 종류나 맛(매운맛, 단맛 등)을 알려주시면 더 좋은 추천을 해드릴 수 있어요."
    
    return {**state, "response": response}


def handle_preference_save(state: ChatState) -> ChatState:
    """선호도 저장 처리 노드"""
    message = state["message"]
    
    # 선호도 키워드 추출
    system_prompt = """사용자 메시지에서 음식 선호도 관련 키워드를 추출하세요.
좋아하는 것, 싫어하는 것, 못 먹는 것 등을 구분해서 추출합니다.
결과는 쉼표로 구분된 키워드만 출력하세요.
예: 매운음식, 한식, 고기"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=message)
    ]
    
    extracted = llm.invoke(messages).content.strip()
    new_keywords = [kw.strip() for kw in extracted.split(",") if kw.strip()]
    
    response = f"알겠어요! '{', '.join(new_keywords)}' 취향을 기억할게요! 📝\n이제 맛집 추천해드릴까요?"
    
    return {
        **state, 
        "response": response,
        "keywords": list(set(state["keywords"] + new_keywords))
    }


def save_context(state: ChatState) -> ChatState:
    """대화 컨텍스트 저장 노드"""
    db = state["db"]
    user_id = state["user_id"]
    message = state["message"]
    response = state["response"]
    summary = state["summary"]
    keywords = state["keywords"]
    
    # 요약 업데이트
    new_summary = f"{summary}\n[User]: {message}\n[Bot]: {response[:100]}..."
    lines = new_summary.strip().split("\n")
    if len(lines) > 10:
        new_summary = "\n".join(lines[-10:])
    
    save_user_summary(db, user_id, new_summary)
    
    # 키워드 저장 (추천 의도였을 경우)
    if state["intent"] == "추천" and keywords:
        save_user_keywords(db, user_id, keywords)
    
    return state


# ============================================
# 라우팅 함수
# ============================================

def route_by_intent(state: ChatState) -> str:
    """의도에 따른 라우팅"""
    intent = state["intent"]
    
    if intent == "추천":
        return "extract_location"
    elif intent == "선호도_질문":
        return "handle_preference_question"
    elif intent == "선호도_저장":
        return "handle_preference_save"
    else:
        return "generate_conversation"


# ============================================
# 그래프 구성
# ============================================

def build_chatbot_graph():
    """LangGraph 워크플로우 구성"""
    
    workflow = StateGraph(ChatState)
    
    # 노드 추가
    workflow.add_node("load_user_context", load_user_context)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("extract_location", extract_location)
    workflow.add_node("rag_search", rag_search)
    workflow.add_node("generate_recommendation", generate_recommendation)
    workflow.add_node("generate_conversation", generate_conversation)
    workflow.add_node("handle_preference_question", handle_preference_question)
    workflow.add_node("handle_preference_save", handle_preference_save)
    workflow.add_node("save_context", save_context)
    
    # 엣지 연결
    workflow.set_entry_point("load_user_context")
    workflow.add_edge("load_user_context", "classify_intent")
    
    # 조건부 라우팅
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "extract_location": "extract_location",
            "handle_preference_question": "handle_preference_question",
            "handle_preference_save": "handle_preference_save",
            "generate_conversation": "generate_conversation"
        }
    )
    
    # 추천 플로우
    workflow.add_edge("extract_location", "rag_search")
    workflow.add_edge("rag_search", "generate_recommendation")
    workflow.add_edge("generate_recommendation", "save_context")
    
    # 대화 플로우
    workflow.add_edge("generate_conversation", "save_context")
    
    # 선호도 플로우
    workflow.add_edge("handle_preference_question", "save_context")
    workflow.add_edge("handle_preference_save", "save_context")
    
    # 종료
    workflow.add_edge("save_context", END)
    
    return workflow.compile()


# 그래프 인스턴스 생성
chatbot_graph = build_chatbot_graph()


# ============================================
# API 엔드포인트용 함수
# ============================================

def generate_chat_response(user: User, message: str, db: Session) -> dict:
    """
    FastAPI 엔드포인트에서 호출하는 메인 함수
    기존 chatbot_chain.py와 동일한 인터페이스 유지
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
        "response": ""
    }
    
    # 그래프 실행
    result = chatbot_graph.invoke(initial_state)
    
    return {"response": result["response"]}
