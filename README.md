# MindFit — 맛집 추천 챗봇 서비스

경기대학교 주변 맛집을 LangGraph 기반 멀티스텝 에이전트로 추천해주는 웹 서비스입니다.  
사용자의 대화 기록을 DB에 저장하여 취향을 학습하고, 누적된 선호도를 기반으로 점점 더 정확한 추천을 제공합니다.

---

## 기술 스택

**Backend**

| 분류 | 기술 |
|------|------|
| 프레임워크 | FastAPI |
| AI/LLM | LangGraph, LangChain, OpenAI GPT-4o-mini |
| 벡터 검색 | FAISS (RAG) |
| ORM | SQLAlchemy 2.0 |
| 마이그레이션 | Alembic |
| 인증 | JWT (PyJWT + bcrypt) |
| 데이터베이스 | MySQL 8.4 (운영) / SQLite (개발) |

**Frontend**

| 분류 | 기술 |
|------|------|
| 프레임워크 | React 18 + Vite |
| 라우팅 | React Router v6 |
| HTTP | Axios |
| 지도 | Google Maps JavaScript API (@react-google-maps/api) |

**Infrastructure**

| 분류 | 기술 |
|------|------|
| 컨테이너 | Docker, Docker Compose |
| 웹서버 | Nginx (프론트 서빙 + API 프록시) |
| 커넥션 풀 | SQLAlchemy pool_pre_ping, pool_size, max_overflow |
| 백업 | mysqldump 기반 논리 백업 자동화 |
| 모니터링 | Slow Query Log, SHOW ENGINE INNODB STATUS |

---

## 주요 기능

**챗봇 (LangGraph 멀티스텝 에이전트)**
- 의도 분류 → 조건부 라우팅 → RAG 검색 → 응답 생성 파이프라인
- 추천 / 대화 / 선호도 질문 / 선호도 저장 4가지 의도 분류
- FAISS 벡터 유사도 검색으로 식당 데이터 RAG 적용
- 유저별 대화 요약(UserSummary)과 키워드(UserKeyword)를 DB에 분리 저장
- 위치 키워드 추출 및 필터링

**식당 데이터**
- 카카오맵 Selenium 크롤링으로 경기대 주변 식당 수집
- Google Places API로 위도/경도, 평점 보강

**지도 연동**
- 챗봇 추천 응답에 식당 위치 정보(위도/경도) 포함
- 프론트엔드 Google Maps에 추천 결과 핀 자동 표시

**인증 및 계정**
- JWT Bearer 토큰 인증
- 최소 권한 원칙(Principle of Least Privilege) 적용 — 앱 계정(DML)과 읽기 전용 계정(SELECT) 분리

**북마크 / 리뷰**
- 식당 북마크 추가/삭제 (다대다 관계)
- 리뷰 작성 및 이미지 업로드 (WebP 변환, 썸네일 자동 생성)

---

## 프로젝트 구조

```
MindFit_Back_Plus/
├── api/v1/
│   ├── endpoints/          # auth, users, restaurants, reviews, bookmarks, chatbot
│   └── routers.py
├── core/
│   ├── config.py           # 환경변수 설정
│   ├── dependencies.py     # DI: get_db, get_current_user, get_admin_user
│   └── security.py         # JWT 발급/검증, bcrypt 해시
├── crud/                   # DB 접근 레이어
├── db/
│   └── database.py         # SQLAlchemy 엔진 + 커넥션 풀 설정
├── models/                 # User, Restaurant, Review, Menu, Keyword, Chatbot, Bookmark
├── schemas/                # Pydantic 스키마 (ChatResponse에 restaurants 포함)
├── services/
│   └── chatbot_chain.py    # LangGraph 에이전트 그래프
├── crawling/
│   ├── crawl_kakao_db.py   # 카카오맵 Selenium 크롤러
│   └── data_crawling.py    # Google Places API 위도/경도 보강
├── infra/mysql/init/       # MySQL 초기화 SQL (읽기 전용 계정 생성)
├── scripts/mysql/          # backup.sh, restore.sh, monitoring.sql
├── static/review_images/   # 업로드 이미지 (original, thumb_300, thumb_750)
├── frontend/               # React + Vite 프론트엔드
├── migrations/             # Alembic 마이그레이션
├── docker-compose.yml      # MySQL + FastAPI + React 통합
├── Dockerfile.backend
└── requirements_docker.txt
```

---

## 챗봇 아키텍처

```
사용자 입력
    │
    ▼
load_user_context     ← DB에서 대화 요약, 선호 키워드 로드
    │
    ▼
classify_intent       ← LLM으로 의도 분류 (추천 / 대화 / 선호도)
    │
    ├─ 추천 ──────► extract_location ──► rag_search ──► generate_recommendation
    ├─ 대화 ──────► generate_conversation
    ├─ 선호도_질문 ► handle_preference_question
    └─ 선호도_저장 ► handle_preference_save
         │
         ▼
    save_context      ← 대화 요약 + 키워드 DB 저장
         │
         ▼
        END
```

---

## 시작하기

### 1. 환경변수 설정

`.env.example`을 복사하여 `.env`를 만들고 키를 입력합니다.

```bash
cp .env.example .env
```

```env
# 개발 (SQLite)
DATABASE_URL=sqlite:///./prac.db

# 운영 (MySQL)
# DATABASE_URL=mysql+pymysql://mindfit_app:mindfit_pass@localhost:3306/mindfit_db?charset=utf8mb4

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### 2. 로컬 개발 실행

```bash
# 백엔드 의존성 설치
conda env create -f environment.yml
# 또는
pip install -r requirements.txt

# DB 마이그레이션
alembic revision --autogenerate
alembic upgrade head

# 식당 데이터 크롤링 (최초 1회)
python crawling/crawl_kakao_db.py
python crawling/data_crawling.py

# 백엔드 실행
uvicorn main:app --reload
```

```bash
# 프론트엔드 (별도 터미널)
cd frontend
npm install
npm run dev
```

| 서비스 | 주소 |
|--------|------|
| 프론트엔드 | http://localhost:3000 |
| 백엔드 API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

### 3. Docker 전체 실행

```bash
docker compose up --build
```

| 서비스 | 주소 |
|--------|------|
| 프론트엔드 | http://localhost:3000 |
| 백엔드 API | http://localhost:8000 |
| MySQL | localhost:3306 |

---

## DB 스키마 주요 관계

```
User ──────────── Review ──────── Restaurant
  │                                   │
  │ (북마크 다대다)                     │
  └──── user_restaurant_bookmarks ────┘
  │
  ├── UserSummary   (대화 요약, 1:1)
  └── UserKeyword   (선호 키워드, 1:N)

Restaurant ──── Menu ──── menu_keywords ──── Keyword
```

---

## MySQL 운영 설정

**커넥션 풀** (`db/database.py`)

```python
pool_pre_ping=True      # 끊어진 커넥션 자동 감지
pool_size=10            # 기본 풀 크기
max_overflow=20         # 최대 초과 커넥션
pool_recycle=1800       # 30분마다 커넥션 재생성
```

**Slow Query Log** — `docker-compose.yml`에 적용됨

```
--slow_query_log=1
--long_query_time=1
```

**백업 / 복구**

```bash
bash scripts/mysql/backup.sh           # backups/mysql/ 에 저장
bash scripts/mysql/restore.sh backups/mysql/<파일명>.sql
```

---

## 계정 권한 구조

| 계정 | 권한 | 용도 |
|------|------|------|
| `mindfit_app` | SELECT, INSERT, UPDATE, DELETE | 애플리케이션 전용 |
| `mindfit_ro` | SELECT | 읽기 전용 모니터링 |

---

## 이미지 업로드 처리

리뷰 이미지는 업로드 시 자동으로 WebP 변환 및 리사이징됩니다.

| 경로 | 용도 | 최대 크기 |
|------|------|-----------|
| `static/review_images/original/` | 원본 | 2048px |
| `static/review_images/thumb_750/` | 중간 썸네일 | 750px |
| `static/review_images/thumb_300/` | 작은 썸네일 | 300px |

---

## API 주요 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/auth/token` | 로그인 (JWT 발급) |
| POST | `/api/v1/users/` | 회원가입 |
| GET | `/api/v1/users/me` | 내 정보 조회 |
| POST | `/api/v1/chatbot/` | 챗봇 메시지 전송 |
| GET | `/api/v1/restaurants/{id}` | 식당 상세 조회 |
| POST | `/api/v1/reviews/restaurant_id={id}` | 리뷰 작성 |
| GET | `/api/v1/bookmarks/` | 북마크 목록 |
| POST | `/api/v1/bookmarks/restaurants/{id}` | 북마크 추가 |
| DELETE | `/api/v1/bookmarks/restaurants/{id}` | 북마크 삭제 |

챗봇 응답 스키마:

```json
{
  "response": "경기옥 추천드려요! ...",
  "restaurants": [
    {
      "id": 1,
      "name": "경기옥",
      "address": "경기도 수원시 장안구 천천동 123",
      "latitude": 37.299,
      "longitude": 127.043,
      "rating": 4.3
    }
  ]
}
```

`restaurants` 배열이 프론트엔드 지도의 핀 표시에 사용됩니다.
