# Chatbot Management Platform

Platform SaaS cho phép người dùng tự tạo và train chatbot từ lịch sử chat.

## 🏗️ Kiến trúc

```
chatbot_management/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── main.py      # FastAPI app
│   └── requirements.txt
│
├── frontend/            # React dashboard
│   └── (sẽ tạo sau)
│
├── database/            # PostgreSQL
│   └── init.sql
│
└── docker-compose.yml   # Orchestration
```

## 🚀 Cài đặt

### Với Docker (Khuyến nghị)

```bash
# Clone project
cd chatbot_management

# Start services
docker-compose up -d

# Access:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:5173
# - API Docs: http://localhost:8000/docs
# - Rasa Server: http://localhost:5005
```

### Không dùng Docker (Windows/Linux/Mac)

#### Cài đặt lần đầu
```bash
# Xem hướng dẫn chi tiết trong:
SETUP_WITHOUT_DOCKER.md
```

#### Khởi động nhanh
```bash
# Windows
start.bat           # Khởi động tất cả services
stop.bat            # Dừng tất cả services

# Linux/Mac/Git Bash
bash start.sh       # Khởi động tất cả services
bash stop.sh        # Dừng tất cả services
```

Script tự động:
- ✅ Kiểm tra PostgreSQL service
- ✅ Kiểm tra database tồn tại
- ✅ Khởi động Backend API (port 8000)
- ✅ Khởi động Rasa Server (port 5005)
- ✅ Khởi động Frontend (port 5173)
- ✅ Mở từng service trong terminal riêng


## 📦 Tính năng

- ✅ User authentication (JWT)
- ✅ Bot CRUD
- ✅ Upload lịch sử chat (JSON)
- ✅ Auto train Rasa models
- ✅ Test chat interface
- ✅ Analytics dashboard

## 🔧 Tech Stack

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React + Vite + Ant Design
- Chatbot Engine: Rasa 3.6.20
- Database: PostgreSQL 14
- Deployment: Docker Compose

## 📚 Tài liệu

- [SETUP_WITHOUT_DOCKER.md](SETUP_WITHOUT_DOCKER.md) - Hướng dẫn cài đặt không dùng Docker
- [RESTART_GUIDE.md](RESTART_GUIDE.md) - Hướng dẫn khởi động lại sau khi tắt máy
- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Hướng dẫn chạy từng service riêng lẻ
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Hướng dẫn setup với Docker (nếu có)

## 🎯 Quick Start Scripts

| Script | Mô tả |
|--------|-------|
| `start.bat` / `start.sh` | Khởi động tất cả services (Backend + Rasa + Frontend) |
| `stop.bat` / `stop.sh` | Dừng tất cả services |
| `docker-compose up -d` | Khởi động với Docker |
| `docker-compose down` | Dừng Docker services |
