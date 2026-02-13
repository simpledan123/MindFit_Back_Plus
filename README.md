# 📌 Tech Stack

## Backend

-   FastAPI
-   SQLAlchemy
-   Alembic
-   JWT Authentication

## Database

-   MySQL 8.4
-   InnoDB Engine
-   UTF8MB4 Character Set
-   Docker 기반 컨테이너 운영

## Schema Design & Modeling

-   관계형 모델 기반 테이블 설계
-   Primary Key / Foreign Key 명시
-   InnoDB 기반 트랜잭션 보장
-   서비스 특성 기반 인덱스 설계

-   모델 구조는 `models/` 디렉토리에서 확인 가능합니다.

## 계정 및 권한 관리 (Security)

최소 권한 원칙(Principle of Least Privilege)을 적용하여 계정을
분리하였습니다.

  계정명        권한                             목적
  ------------- -------------------------------- --------------------
  mindfit_app   SELECT, INSERT, UPDATE, DELETE   애플리케이션 전용
  mindfit_ro    SELECT                           읽기 전용 모니터링

``` sql
CREATE USER 'mindfit_ro'@'%' IDENTIFIED BY 'password';
GRANT SELECT ON mindfit_db.* TO 'mindfit_ro'@'%';
FLUSH PRIVILEGES;
```

## 성능 모니터링 및 최적화

운영 환경을 가정하여 성능 모니터링 기능을 구성하였습니다.

### Slow Query Log 활성화

-   slow_query_log = 1
-   long_query_time = 1

``` sql
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
```

### 세션 및 상태 점검

``` sql
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS;
```
## 백업 및 복구 전략

MySQL `mysqldump` 기반 논리 백업을 자동화하였습니다.

### ✔ 백업

``` bash
bash scripts/mysql/backup.sh
```

### ✔ 복구

``` bash
bash scripts/mysql/restore.sh backups/mysql/<backup_file>.sql
```

적용 옵션: - --single-transaction - 루틴 및 이벤트 포함 - 백업/복구
테스트 완료

## Connection Pool 설정

운영 환경을 고려하여 SQLAlchemy Connection Pool 옵션을 적용하였습니다.

-   pool_pre_ping=True
-   pool_size
-   max_overflow
-   pool_recycle

장기 실행 환경에서 커넥션 안정성을 확보하기 위한 설정입니다.


---  

## ⚙️ 환경변수 (.env)

.env 에 KEY를 꼭 추가해주세요

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
python crawling/crawl_kakao_db.py
```
카카오맵으로 경기대 근처 맛집을 크롤링해서 저장합니다.

```
python crawling/data_crawling.py
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
---

## 📢 주의사항

- `.env` 파일을 반드시 세팅해야 서버가 정상 작동합니다.
- Google Places API 키가 필요합니다.
- OpenAI API 키가 필요합니다.

## 🐬 MySQL로 실행하기

### MySQL 컨테이너 실행  
docker compose -f docker-compose.mysql.yml up -d