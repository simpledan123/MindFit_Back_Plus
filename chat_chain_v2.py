import os
import sqlite3
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# DB 연결 및 식당 정보 로딩
conn = sqlite3.connect("prac.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name, latitude, longitude, rating, kakao_rating, address, phone FROM restaurants")
rows = cursor.fetchall()

# Document 생성
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
        Document(
            page_content=content,
            metadata={
                "id": id_,
                "latitude": lat,
                "longitude": lng,
                "rating": rating,
                "kakao_rating": kakao_rating
            }
        )
    )

# 텍스트 분할 및 벡터 DB 생성
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

try:
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = FAISS.from_documents(docs, embeddings)

    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=db.as_retriever(),
        return_source_documents=True
    )
    print("✅ LangChain 초기화 완료")

except Exception as e:
    print(f"❌ LangChain 초기화 실패: {e}")
    qa_chain = None

# 챗봇 호출 함수
def generate_chat_response(query):
    if qa_chain is None:
        return {"answer": "❌ 챗봇 초기화 실패: 관리자에게 문의하세요.", "metadata": {}}
    
    result = qa_chain({"query": query})
    answer = result["result"]
    metadata = {}

    if result["source_documents"]:
        top_doc = result["source_documents"][0]
        metadata = {
            "id": top_doc.metadata['id'],
            "latitude": top_doc.metadata['latitude'],
            "longitude": top_doc.metadata['longitude'],
            "rating": top_doc.metadata['rating'],
            "kakao_rating": top_doc.metadata['kakao_rating']
        }

    return {"answer": answer, "metadata": metadata}
