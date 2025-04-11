import os
import sqlite3
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 환경변수 로드
load_dotenv()

# OpenAI API 키 설정
openai_api_key = os.getenv("OPENAI_API_KEY")

# 데이터베이스 연결
conn = sqlite3.connect("prac.db")
cursor = conn.cursor()

# 📌 id, name, latitude, longitude, rating까지 가져오기
cursor.execute("SELECT id, name, latitude, longitude, rating, address, phone FROM restaurants")
rows = cursor.fetchall()

# 문서 생성
documents = []
for row in rows:
    id_, name, lat, lng, rating, address, phone = row
    content = f"식당명: {name}\n주소: {address}\n전화번호: {phone}"
    documents.append(
        Document(
            page_content=content,
            metadata={
                "id": id_,
                "latitude": lat,
                "longitude": lng,
                "rating": rating
            }
        )
    )

# 문서 분할
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# 벡터 스토어 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
db = FAISS.from_documents(docs, embeddings)

# 📌 RetrievalQA 체인 설정 (source_documents 반환)
llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=db.as_retriever(),
    return_source_documents=True  # ★ 요거 추가해서 source 가져오기
)

# 대화 루프
while True:
    query = input("질문을 입력하세요 (종료하려면 '종료' 입력): ")
    if query.lower() == "종료":
        break

    # run이 아니라 __call__ 사용
    result = qa_chain({"query": query})

    # 답변 출력
    print("\n=== 답변 ===")
    print(result["result"])  # 자연스러운 답변 문장

    # 추천에 사용된 실제 문서 메타데이터 출력
    source_docs = result["source_documents"]

    if source_docs:
        top_doc = source_docs[0]  # 가장 연관 높은 식당 하나
        print("\n=== 추가 정보 (MetaData) ===")
        print(f"식당 ID: {top_doc.metadata['id']}")
        print(f"위도 (Latitude): {top_doc.metadata['latitude']}")
        print(f"경도 (Longitude): {top_doc.metadata['longitude']}")
        print(f"평점 (Rating): {top_doc.metadata['rating']}")
        print("========================\n")
    else:
        print("추가 정보를 찾을 수 없습니다.\n")
