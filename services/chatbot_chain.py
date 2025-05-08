from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.schema import SystemMessage, HumanMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document

from dotenv import load_dotenv
import os

from crud.chatbot import get_user_summary, save_user_summary, save_user_keywords
from models.user import User
from sqlalchemy.orm import Session

# 환경설정
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# LangChain 구성
llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
memory = ConversationSummaryMemory(llm=llm, return_messages=True)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# 식당 정보 벡터화
import sqlite3
conn = sqlite3.connect("prac.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name, latitude, longitude, rating, kakao_rating, address, phone FROM restaurants")
rows = cursor.fetchall()
documents = []
for row in rows:
    id_, name, lat, lng, rating, kakao_rating, address, phone = row
    content = f"""식당명: {name}
주소: {address}
전화번호: {phone}
카카오 평점: {kakao_rating}
구글 평점: {rating}
"""
    documents.append(
        Document(page_content=content, metadata={
            "id": id_, "latitude": lat, "longitude": lng,
            "rating": rating, "kakao_rating": kakao_rating
        })
    )
docs = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(documents)
vectorstore = FAISS.from_documents(docs, embeddings)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever(), return_source_documents=True)

# 핵심 함수
def extract_keywords_from_summary(summary: str) -> list[str]:
    messages = [
        SystemMessage(content="다음 요약에서 사용자의 음식 취향을 나타내는 핵심 키워드 3~5개만 쉼표로 추출해줘."),
        HumanMessage(content=summary)
    ]
    result = llm(messages).content.strip()
    return [kw.strip() for kw in result.split(",") if kw.strip()]

def classify_intent(query: str, summary: str) -> str:
    messages = [
        SystemMessage(content=f"""이 사용자의 요약 정보: {summary}
사용자 질문의 의도를 분류해줘:
1. 메뉴추천
2. 식당추천
3. 정보입력
위 세 가지 중 하나만 말해줘."""),
        HumanMessage(content=query)
    ]
    return llm(messages).content.strip()

def generate_chat_response(query: str, user: User, db: Session):
    if qa_chain is None:
        return {"answer": "❌ 챗봇 초기화 실패: 관리자에게 문의하세요."}

    summary_obj = get_user_summary(db, user.id)
    summary = summary_obj.summary if summary_obj else ""
    intent = classify_intent(query, summary)

    if intent == "정보입력":
        memory.save_context({"input": query}, {"output": "입력 완료!"})
        updated_summary = memory.predict_new_summary(memory.chat_memory.messages, summary)
        keywords = extract_keywords_from_summary(updated_summary)
        save_user_keywords(db, user.id, keywords)
        save_user_summary(db, user.id, updated_summary)
        return {"answer": f"당신의 선호를 저장했어요: {', '.join(keywords)}"}

    elif intent == "식당추천":
        result = qa_chain({"query": query})
        return {"answer": result["result"]}

    elif intent == "메뉴추천":
        menu = query.replace("먹고싶어", "").strip()
        result = qa_chain({"query": f"{menu} 잘하는 집 알려줘"})
        return {"answer": result["result"]}

    else:
        return {"answer": "죄송해요, 질문을 이해하지 못했어요. 다시 말해주시겠어요?"}
