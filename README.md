# MindFit — 프론트엔드 + Docker 통합 패키지

이 패키지는 기존 MindFit_Back_Plus 레포에 추가할 파일들입니다.

---

## 📁 파일 배치 방법

```
MindFit_Back_Plus/          ← 기존 레포 루트
├── frontend/               ← ✅ 이 폴더 통째로 복사
├── docker-compose.yml      ← ✅ 기존 파일 교체
├── Dockerfile.backend      ← ✅ 새로 추가
├── requirements_docker.txt ← ✅ 새로 추가
│
├── schemas/chat.py         ← ✅ backend_changes/schemas/chat.py 내용으로 교체
└── services/chatbot_chain.py ← ✅ backend_changes/services/chatbot_chain.py 내용으로 교체
```

---

## ⚙️ 환경변수 설정 (.env)

기존 `.env`에 아래 항목이 모두 있는지 확인하세요:

```env
DATABASE_URL=mysql+pymysql://mindfit_app:mindfit_pass@localhost:3306/mindfit_db?charset=utf8mb4

JWT_SECRET_KEY=secretkey
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key   ← 프론트 지도에 사용됨
```

---

## 🚀 실행 방법

### 로컬 개발 (백엔드만)
```bash
# 백엔드
uvicorn main:app --reload

# 프론트엔드 (별도 터미널)
cd frontend
npm install
npm run dev       # http://localhost:3000
```

### Docker 전체 실행
```bash
docker compose up --build
```

접속:
- 프론트엔드: http://localhost:3000
- 백엔드 Swagger: http://localhost:8000/docs

---

## 🗺️ 지도 연동 구조

챗봇이 "추천" 의도를 감지하면:
1. RAG 검색으로 식당 위도/경도 포함 데이터 반환
2. API 응답에 `restaurants` 배열 포함
3. 프론트에서 Google Maps에 핀 자동 표시

---

## 📝 변경된 백엔드 파일

| 파일 | 변경 내용 |
|------|----------|
| `schemas/chat.py` | `ChatResponse`에 `restaurants` 필드 추가 |
| `services/chatbot_chain.py` | `generate_chat_response` 반환값에 식당 위치 목록 포함 |
