# Setup Chatbot Management System (Without Docker)

Hướng dẫn cài đặt và chạy dự án trên máy local không sử dụng Docker.

## Yêu cầu hệ thống

### 1. Python 3.10+
```bash
# Kiểm tra version
python --version  # hoặc python3 --version
```

### 2. Node.js 18+ và npm
```bash
# Kiểm tra version
node --version
npm --version
```

### 3. PostgreSQL 14+
- Download và cài đặt từ: https://www.postgresql.org/download/
- Hoặc sử dụng PostgreSQL có sẵn trên hệ thống

---

## Bước 1: Setup Database (PostgreSQL)

### 1.1. Tạo Database và User

```bash
# Đăng nhập vào PostgreSQL
psql -U postgres

# Tạo user và database
CREATE USER chatbot_user WITH PASSWORD 'chatbot_pass';
CREATE DATABASE chatbot_db OWNER chatbot_user;
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;

# Thoát
\q
```

### 1.2. Chạy Migration với Alembic

**Lưu ý:** Dự án sử dụng Alembic để quản lý database migrations thay vì raw SQL.

Migrations sẽ được chạy tự động khi start backend server (bước 2.4), hoặc bạn có thể chạy thủ công:

```bash
# Windows:
migrate.bat upgrade

# Linux/Mac:
./migrate.sh upgrade
```

Hoặc chạy trực tiếp với Alembic:

```bash
cd backend
alembic upgrade head
```

**Kiểm tra migration status:**
```bash
# Windows:
migrate.bat current

# Linux/Mac:
./migrate.sh current
```

Xem thêm chi tiết tại: [MIGRATIONS.md](MIGRATIONS.md)

---

## Bước 2: Setup Backend (FastAPI)

### 2.1. Tạo Virtual Environment

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2.2. Cài đặt Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3. Cấu hình Environment Variables

Tạo file `.env` trong thư mục `backend/`:

```env
# Database
DATABASE_URL=postgresql://chatbot_user:chatbot_pass@localhost:5432/chatbot_db

# Security
SECRET_KEY=your-secret-key-change-this-in-production-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rasa
RASA_SERVER_URL=http://localhost:5005
```

### 2.4. Chạy Database Migrations

```bash
# Từ thư mục backend/
alembic upgrade head
```

Hoặc sử dụng script tiện lợi từ root folder:
```bash
# Windows:
migrate.bat upgrade

# Linux/Mac:
./migrate.sh upgrade
```

### 2.5. Chạy Backend Server

```bash
# Từ thư mục backend/
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend sẽ chạy tại: **http://localhost:8000**

**Lưu ý:** Backend sẽ tự động kết nối đến PostgreSQL. Đảm bảo database đã được tạo và migrations đã chạy (bước 2.4).

---

## Bước 3: Quản lý Database Migrations (Optional)

### 3.1. Các lệnh Alembic thường dùng

```bash
# Xem current migration version
migrate.bat current        # Windows
./migrate.sh current       # Linux/Mac

# Xem lịch sử migrations
migrate.bat history
./migrate.sh history

# Tạo migration mới (manual)
migrate.bat create add_new_feature
./migrate.sh create add_new_feature

# Auto-generate migration từ SQLAlchemy models
migrate.bat autogenerate describe_changes
./migrate.sh autogenerate describe_changes

# Rollback migration
migrate.bat downgrade
./migrate.sh downgrade
```

### 3.2. Workflow khi thay đổi Database Schema

1. **Cập nhật SQLAlchemy models** trong `backend/app/models/`
2. **Auto-generate migration:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "describe your changes"
   ```
3. **Review migration file** trong `backend/alembic/versions/`
4. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

Xem chi tiết tại: [MIGRATIONS.md](MIGRATIONS.md)

---

## Bước 4: Setup Rasa Server

### 4.1. Tạo Virtual Environment riêng cho Rasa

```bash
cd rasa

# Tạo virtual environment
python -m venv venv_rasa

# Kích hoạt
# Windows:
venv_rasa\Scripts\activate
# Linux/Mac:
source venv_rasa/bin/activate
```

### 4.2. Cài đặt Rasa

```bash
pip install rasa==3.6.20
```

### 4.3. Train Model mẫu (Optional)

```bash
# Từ thư mục rasa/
rasa train
```

### 4.4. Chạy Rasa Server

**Cấu hình Environment Variables:**

Tạo file `.env` trong thư mục `rasa/` (hoặc copy từ `.env.example`):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chatbot_db
DB_USER=chatbot_user
DB_PASSWORD=chatbot_pass
```

**Chạy Rasa:**

```bash
# Từ thư mục rasa/
# Đảm bảo đã load env vars (tự động khi dùng start.sh/start.bat)

rasa run --enable-api --cors "*" --port 5005
```

**Lưu ý:** 
- File `.env` đã được tạo sẵn với giá trị mặc định
- Script `start.sh` và `start.bat` sẽ tự động load file `.env`
- Nếu chạy thủ công, cần set env vars trước (xem `.env.example`)

Rasa server sẽ chạy tại: **http://localhost:5005**

---

## Bước 5: Setup Frontend (React + Vite)

### 5.1. Cài đặt Dependencies

```bash
cd frontend
npm install
```

### 5.2. Cấu hình API URL

Tạo file `.env` trong thư mục `frontend/`:

```env
VITE_API_URL=http://localhost:8000/api
```

Hoặc cập nhật `frontend/src/api/axios.js` nếu cần:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

### 5.3. Chạy Development Server

```bash
# Từ thư mục frontend/
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:5173**

---

## Bước 6: Kiểm tra hệ thống

### 6.1. Kiểm tra các service đang chạy

- PostgreSQL: `localhost:5432`
- Backend API: `http://localhost:8000`
- Rasa Server: `http://localhost:5005`
- Frontend: `http://localhost:5173`

### 6.2. Test API

```bash
# Health check backend
curl http://localhost:8000/

# Health check Rasa
curl http://localhost:5005/
```

### 6.3. Truy cập ứng dụng

Mở trình duyệt và truy cập: **http://localhost:5173**

---

## Workflow làm việc hàng ngày

### Start tất cả services

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Chạy migrations (nếu có thay đổi)
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Rasa:**
```bash
cd rasa
venv_rasa\Scripts\activate  # Windows
# source venv_rasa/bin/activate  # Linux/Mac

# Environment variables will be loaded automatically from rasa/.env
# Or you can load manually:
# Windows: for /f "tokens=*" %a in (rasa\.env) do set %a
# Linux/Mac: export $(cat rasa/.env | grep -v '^#' | xargs)

rasa run --enable-api --cors "*" --port 5005
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## Troubleshooting

### 1. Lỗi kết nối Database

```bash
# Kiểm tra PostgreSQL đang chạy
# Windows:
pg_ctl status

# Linux:
systemctl status postgresql

# Mac:
brew services list | grep postgresql
```

### 2. Lỗi Port đã được sử dụng

```bash
# Windows - Tìm process đang dùng port
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill process
# Windows:
taskkill /PID <PID> /F
# Linux/Mac:
kill -9 <PID>
```

### 3. Lỗi Import Python packages

```bash
# Đảm bảo đang ở đúng virtual environment
# Cài lại dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Rasa model không load được

```bash
# Train lại model
cd rasa
rasa train

# Kiểm tra model đã được tạo
ls models/
```

### 5. Frontend không kết nối được Backend

- Kiểm tra CORS settings trong `backend/app/main.py`
- Đảm bảo `VITE_API_URL` đúng trong frontend `.env`
- Clear browser cache và hard refresh (Ctrl+Shift+R)

---

## Tính năng chính

1. ✅ Quản lý Bots (Tạo, sửa, xóa)
2. ✅ Upload Training Data (JSON, CSV, TXT, YAML, Markdown)
3. ✅ Train Bot với Rasa NLU
4. ✅ Chat với Bot (Session-based)
5. ✅ Theo dõi lịch sử hội thoại
6. ✅ Intent detection & Confidence score
7. ✅ Multi-user support với JWT authentication

---

## Cấu trúc thư mục

```
chatbot_management/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helper functions
│   ├── requirements.txt
│   └── .env
├── frontend/               # React application
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── contexts/      # React contexts
│   ├── package.json
├── database/             # SQL scripts (deprecated - chỉ reference)
└── alembic/             # Alembic migrations (hiện tại)
    ├── versions/        # Migration files
    │   ├── 001_initial.py
    │   └── 002_triggers.py
    └── env.py          # Alembic config
│   ├── models/           # Trained models
│   └── config.yml        # Rasa configuration
└── database/             # SQL scripts
- **Development**: Tất cả services chạy với hot-reload
- **Production**: Cần build frontend (`npm run build`) và deploy với nginx/apache
- **Database**: 
  - Sử dụng Alembic cho migrations (không dùng raw SQL nữa)
  - Backup định kỳ với `pg_dump`
  - Migration files: `backend/alembic/versions/`
- **Rasa Models**: Lưu trong thư mục `backend/models/` để persistent storage
---

Nếu gặp vấn đề, kiểm tra:
1. Logs của từng service
2. Database connection string
3. Port conflicts
4. Virtual environment activation
5. Environment variables
6. Alembic migration status (`alembic current`)

**Tài liệu tham khảo:**
- [MIGRATIONS.md](MIGRATIONS.md) - Hướng dẫn chi tiết về Alembic
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Hướng dẫn chuyển đổi từ raw SQL

Chúc bạn setup thành công! 🎉

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Logs của từng service
2. Database connection string
3. Port conflicts
4. Virtual environment activation
5. Environment variables

Chúc bạn setup thành công! 🎉
