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
openai_api_key = os.getenv("여기에 당신의 키를 입력하세용")

# 1. DB에서 식당 데이터 불러오기 + 후문/정문 데이터 추가
def load_restaurant_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name, phone, opening_hours, rating FROM restaurants")
    rows = cursor.fetchall()

    documents = []
    for row in rows:
        name, phone, opening_hours, rating = row
        text = f"식당 이름: {name}\n전화번호: {phone}\n영업시간: {opening_hours}\n평점: {rating}"
        documents.append(Document(page_content=text))

    # 추가: 후문/정문 정보
    extra_text = (
        "정문 위치: 위도 37.301778, 경도 127.034235\n"
        "후문 위치: 위도 37.297540, 경도 127.041462\n"
    )
    documents.append(Document(page_content=extra_text))

    conn.close()
    return documents

# 2. 텍스트 분할
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

# 3. 벡터스토어 만들기
def create_vectorstore(documents):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore

# 4. 챗봇 QA 체인 만들기
def create_qa_chain(vectorstore):
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo")
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
    return qa_chain

def main():
    # DB 파일 경로
    db_path = "./prac.db"

    print("DB에서 식당 정보 불러오는 중...")
    documents = load_restaurant_data(db_path)

    print("텍스트 분할 중...")
    split_docs = split_documents(documents)

    print("벡터스토어 생성 중...")
    vectorstore = create_vectorstore(split_docs)

    print("챗봇 준비 완료!")

    qa_chain = create_qa_chain(vectorstore)

    # 챗봇 루프
    while True:
        query = input("\n질문을 입력하세요 (종료하려면 'exit' 입력): ")
        if query.lower() == "exit":
            print("챗봇을 종료합니다.")
            break
        result = qa_chain.run(query)

        # fallback 처리 추가
        if not result or len(result.strip()) < 5:
            print("\n답변: 죄송합니다. 질문을 이해하지 못했습니다. 다시 질문해 주세요.")
        else:
            print("\n답변:", result)

if __name__ == "__main__":
    main()
