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

```bash
# Clone project
cd chatbot_management

# Start services
docker-compose up -d

# Access:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

## 📦 Tính năng

- ✅ User authentication (JWT)
- ✅ Bot CRUD
- ✅ Upload lịch sử chat (JSON)
- ✅ Auto train Rasa models
- ✅ Test chat interface
- ✅ Analytics dashboard

## 🔧 Tech Stack

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React + Ant Design
- Chatbot Engine: Rasa 3.6.20
- Database: PostgreSQL 14
