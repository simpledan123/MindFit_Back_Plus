# MindFit_Backend_plus 🧠

FastAPI + Crawling + Database Integration Project

---

## 📦 프로젝트 소개

MindFit_plus는 FastAPI 서버와 웹 크롤링 기능을 통합한 프로젝트입니다.  
크롤링한 식당 데이터를 데이터베이스에 저장하고, API를 통해 조회할 수 있습니다.
그리고 그 데이터를 이용해 간단한 챗봇을 사용할 수 있습니다.

본 프로젝트는 다음 두 레포지토리를 기반으로 병합하여 개발되었습니다.

- API 서버 구축: [minemine0961/MindFit_back](https://github.com/minemine0961/MindFit_back)
- 웹 크롤링: [leekiin/MindFit](https://github.com/leekiin/MindFit)

MindFit_plus는 minemine0961의 FastAPI 기반 API 서버를 중심으로, leekiin의 웹 크롤링 기능을 통합하여 하나의 백엔드 프로젝트로 재구성되었습니다.

또한 여기에 simpledan123이 챗봇 기능을 추가했습니다.

데이터 크롤링->db에 저장->해당 db를 베이스로 챗봇 작동

---

## 🛠️ 설치 방법

### 1. 클론

```bash
git clone https://github.com/yourname/MindFit_plus.git
cd MindFit_plus
```

또는 Download Zip 해서 코드 다운받아도 됨

### 2. 가상환경 세팅

- **conda 사용 시**

```bash
conda env create -f environment.yml
conda activate mindfit
```

- **venv 사용 시**

```bash
python -m venv venv
venv\Scripts\activate     # (Windows)

pip install -r requirements.txt
#가상환경을 구성하지 않고 작업하려면 pip install -r requirements.txt 이것만 실행
```

---

## ⚙️ 환경변수 (.env)

먼저 프로젝트 루트에 `.env` 파일을 만들어야 합니다.  

.env 에 KEY를 꼭 추가해주세요!  

내용은 다음과 같이 적어주세요:

```env
DATABASE_URL = sqlite:///./prac.db

JWT_SECRET_KEY = secretkey
JWT_ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 10
OPENAI_API_KEY=여기에 당신의 키를 입력하세용
GOOGLE_MAPS_API_KEY=키입력
```

---

## 🗄️ 데이터베이스 초기 세팅

```bash
alembic revision --autogenerate
alembic upgrade head
```

## 🌐 크롤링 스크립트 실행

```bash
python crawling/kakao_crawl_db.py
```
카카오맵으로 경기대 근처 맛집을 크롤링해서 저장합니다.

```
python data_crawling.py
```

- 카카오맵으로 크롤링할 수 없는 정보(위도, 경도 등)을 구글 API를 이용해서 크롤링한 후, 카카오 기반으로 크롤링해서 저장한 맛집 DB에 추가합니다.  

- 경기대 주변 식당 데이터를 크롤링하고 데이터베이스에 저장합니다. 위에서부터 순서대로 실행시켜야 합니다!

---

## 🛰️ 서버 실행

```bash
uvicorn main:app --reload
```

- 서버 주소: http://localhost:8000
- Swagger 문서: http://localhost:8000/docs

---

## 🧠 챗봇 기능 실행

챗봇은 서버를 켜면 자동으로 같이 켜집니다!  
현재는 백엔드에서 동작합니다.  
Swagger UI에서 default/chat 들어가서, Try it out 누르고 {"message": "경기대 근처 맛집 추천해줘"} 이런식으로 작동  

- 크롤링된 데이터를 기반으로 챗봇이 작동합니다.

---

## 📚 주요 기능

- Google Places API를 이용한 식당 정보 크롤링
- FastAPI 서버를 통한 데이터 조회 및 관리
- SQLite 데이터베이스 연동

---

## 📢 주의사항

- `.env` 파일을 반드시 세팅해야 서버가 정상 작동합니다.
- Google Places API 키가 필요합니다.
- OpenAI API 키가 필요합니다.

