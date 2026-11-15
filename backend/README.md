# Getting Started Todo App - FastAPI Backend

FastAPI 및 Uvicorn 기반의 비동기(Async) Python Todo App 백엔드 서버입니다.  
SQLite 및 MySQL 데이터베이스와의 비동기 연동을 지원하며, React 기반 프론트엔드(`client`) 및 Nginx 리버스 프록시와 완벽하게 연동됩니다.

---

## 🛠️ 기술 스택 (Tech Stack)

- **언어 및 런타임**: Python 3.10+
- **웹 프레임워크**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI 서버**: [Uvicorn](https://www.uvicorn.org/)
- **데이터 검증/직렬화**: [Pydantic v2](https://docs.pydantic.dev/)
- **비동기 DB 클라이언트**: 
  - [aiosqlite](https://github.com/omnilib/aiosqlite) (SQLite)
  - [aiomysql](https://github.com/aio-libs/aiomysql) (MySQL)
- **테스트 프레임워크**: [pytest](https://docs.pytest.org/), `pytest-asyncio`, `httpx`

---

## 📁 디렉토리 구조 (Project Structure)

```text
backend/
├── src/
│   ├── main.py              # FastAPI 메인 앱 및 라이프사이클(Lifespan) 관리
│   ├── models.py            # Pydantic 데이터 모델 (Item, ItemCreate 등)
│   ├── persistence/         # 비동기 데이터베이스 계층
│   │   ├── __init__.py      # DB 엔진 자동 선택 (SQLite / MySQL)
│   │   ├── sqlite.py        # aiosqlite 기반 SQLite 구현
│   │   └── mysql.py         # aiomysql 기반 MySQL 풀 구현
│   └── routes/              # API 라우터
│       ├── __init__.py
│       ├── greeting.py      # /api/greeting 라우트
│       └── items.py         # /api/items CRUD 라우트
├── spec/                    # pytest 기반 비동기 단위/통합 테스트
│   ├── persistence/
│   └── routes/
├── Dockerfile               # 컨테이너 빌드 파일
├── main.py                  # 진입점 스크립트
├── pytest.ini               # pytest 설정 파일
├── requirements.txt         # Python 의존성 패키지 목록
└── README.md                # 백엔드 설명 문서
```

---

## 🚀 설치 및 로컬 실행 방법 (Getting Started)

### 1. 가상환경(venv) 생성 및 활성화

#### Windows (PowerShell)
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Windows (CMD)
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
```

#### macOS / Linux
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2. 패키지 의존성 설치

```bash
uv pip install -r requirements.txt
```

---

### 3. 서버 실행

기본 포트인 **`3000`** 번 포트로 서버가 기동됩니다.

#### 방법 1: `uvicorn` 명령어로 직접 실행 (코드 수정 시 자동 재시작 지원)
```bash
uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload
```

#### 방법 2: `main.py` 실행
```bash
python main.py
```

- 서버 주소: `http://localhost:3000`
- **Swagger UI (대화형 API 문서)**: `http://localhost:3000/docs`
- **Redoc 문서**: `http://localhost:3000/redoc`

---

## 🗄️ 데이터베이스 설정 (Database Configuration)

환경변수를 통해 데이터베이스를 유연하게 설정할 수 있습니다.

### SQLite (기본값)
`MYSQL_HOST` 환경변수가 설정되지 않은 경우 기본적으로 SQLite를 사용합니다.

- `SQLITE_DB_LOCATION`: SQLite 데이터베이스 파일 경로 (기본값: `/etc/todos/todo.db` 또는 로컬 지정 경로)
- 로컬 경로 지정 예시:
  ```powershell
  # Windows PowerShell
  $env:SQLITE_DB_LOCATION = "./todo.db"
  python main.py
  ```

### MySQL
`MYSQL_HOST` 또는 `MYSQL_HOST_FILE` 환경변수가 설정되어 있으면 자동으로 MySQL 비동기 모드로 전환됩니다.

| 환경변수명 | Docker Secret 파일 변수명 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `MYSQL_HOST` | `MYSQL_HOST_FILE` | `localhost` | MySQL 서버 호스트명 또는 IP |
| `MYSQL_USER` | `MYSQL_USER_FILE` | `root` | MySQL 사용자명 |
| `MYSQL_PASSWORD` | `MYSQL_PASSWORD_FILE` | `""` | MySQL 비밀번호 |
| `MYSQL_DB` | `MYSQL_DB_FILE` | `todos` | 데이터베이스 이름 |

---

## 📡 API 엔드포인트 명세 (API Specification)

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/greeting` | 인사말 조회 | - | `{"greeting": "Hello world!"}` |
| `GET` | `/api/items` | 전체 Todo 목록 조회 | - | `[{"id": "...", "name": "...", "completed": false}, ...]` |
| `POST` | `/api/items` | 새 Todo 항목 추가 | `{"name": "할 일 내용"}` | `{"id": "UUID", "name": "할 일 내용", "completed": false}` |
| `PUT` | `/api/items/{id}` | Todo 항목 수정 | `{"name": "수정 이름", "completed": true}` | `{"id": "UUID", "name": "수정 이름", "completed": true}` |
| `DELETE` | `/api/items/{id}` | Todo 항목 삭제 | - | `HTTP 200 OK` |

---

## 🧪 테스트 실행 (Running Tests)

`pytest`를 사용하여 영속성 계층 및 API 라우트에 대한 비동기 단위 테스트를 실행합니다.

```bash
# 전체 테스트 실행
pytest

# 상세 출력 모드로 실행
pytest -v
```

---

## 🐳 Docker 컨테이너 빌드 및 실행

```bash
# Docker 이미지 빌드
docker build -t todo-backend-fastapi .

# SQLite 모드로 컨테이너 실행
docker run -dp 3000:3000 todo-backend-fastapi
```
