# 🚀 Chatbot Management Platform - Hướng Dẫn Sử Dụng

## 📋 Tổng Quan

Platform SaaS cho phép người dùng tự tạo và train chatbot từ lịch sử chat.

### Tính Năng Chính

✅ User authentication (JWT)
✅ Bot CRUD management
✅ Upload training data (JSON)
✅ Auto train Rasa models
✅ Test chat interface
✅ Dashboard & Analytics
✅ React Frontend với Ant Design

## 🏃 Quick Start

### 1. Development Mode

#### Backend + Database + Rasa:
```bash
cd chatbot_management
docker-compose up -d postgres backend rasa
```

#### Frontend (Development Server):
```bash
cd frontend
npm install
npm run dev
```

Truy cập:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. Production Mode (Docker)

```bash
# Build và chạy tất cả services
docker-compose up -d --build

# Hoặc chỉ rebuild frontend
docker-compose up -d --build frontend
```

Truy cập:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 📖 Sử Dụng Platform

### 1. Đăng Ký & Đăng Nhập

1. Mở http://localhost:5173
2. Click "Đăng ký ngay"
3. Điền thông tin: Email, Họ tên, Mật khẩu
4. Đăng nhập với tài khoản vừa tạo

### 2. Tạo Bot

1. Vào menu "My Bots"
2. Click "Create Bot"
3. Nhập:
   - Bot Name: Tên bot của bạn
   - Description: Mô tả (tùy chọn)
   - Language: vi (Vietnamese) hoặc en (English)
4. Click OK

### 3. Upload Training Data

1. Vào menu "Training Data"
2. Chọn bot từ dropdown
3. Click "Download Template" để tải mẫu JSON
4. Chỉnh sửa file JSON theo format:

```json
[
  {
    "user": "Xin chào",
    "bot": "Xin chào! Tôi có thể giúp gì cho bạn?",
    "intent": "greeting"
  },
  {
    "user": "Giá bao nhiêu?",
    "bot": "Sản phẩu này giá 299.000đ",
    "intent": "price_inquiry"
  }
]
```

5. Click "Upload Training Data" và chọn file JSON

### 4. Train Bot

1. Quay lại "My Bots"
2. Click nút "Train" trên bot đã upload data
3. Đợi 30-60 giây cho quá trình training
4. Status sẽ chuyển từ "DRAFT" → "TRAINING" → "ACTIVE"

### 5. Test Chat

**Cách 1:** Từ Bot List
1. Click nút "Chat" trên bot có status ACTIVE

**Cách 2:** Từ Menu
1. Vào menu "Test Chat"
2. Chọn bot từ dropdown
3. Gõ tin nhắn và nhấn Enter hoặc Send
4. Bot sẽ trả lời theo training data

## 🗂️ Cấu Trúc Project

```
chatbot_management/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/         # REST API endpoints
│   │   │   ├── auth.py      # Authentication
│   │   │   ├── bots.py      # Bot management
│   │   │   ├── chat.py      # Chat & training
│   │   │   └── training.py  # Training data
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   │   ├── rasa_service.py     # Rasa chat
│   │   │   └── rasa_training.py    # Auto training
│   │   ├── auth.py      # JWT authentication
│   │   ├── database.py  # DB config
│   │   ├── schemas.py   # Pydantic models
│   │   └── main.py      # FastAPI app
│   └── Dockerfile
│
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── api/        # API services
│   │   │   ├── axios.js     # Axios config
│   │   │   ├── auth.js      # Auth API
│   │   │   ├── bots.js      # Bots API
│   │   │   └── training.js  # Training API
│   │   ├── components/  # Reusable components
│   │   ├── contexts/    # React contexts
│   │   │   └── AuthContext.jsx
│   │   ├── layouts/     # Page layouts
│   │   │   └── DashboardLayout.jsx
│   │   ├── pages/       # Page components
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardHome.jsx
│   │   │   ├── BotsPage.jsx
│   │   │   ├── TrainingDataPage.jsx
│   │   │   └── ChatPage.jsx
│   │   ├── App.jsx      # Main app
│   │   └── main.jsx     # Entry point
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── database/
│   └── init.sql         # Database schema
│
└── docker-compose.yml   # Docker orchestration
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký user mới
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Lấy thông tin user hiện tại

### Bots
- `GET /api/bots/` - Lấy danh sách bots
- `POST /api/bots/` - Tạo bot mới
- `GET /api/bots/{id}` - Chi tiết bot
- `PUT /api/bots/{id}` - Cập nhật bot
- `DELETE /api/bots/{id}` - Xóa bot

### Training
- `GET /api/bots/{id}/training/` - Lấy training data
- `POST /api/bots/{id}/training/upload` - Upload file JSON
- `DELETE /api/bots/{id}/training/{data_id}` - Xóa training data
- `POST /api/bots/{id}/train` - Trigger training
- `GET /api/bots/{id}/training/sessions` - Lịch sử training

### Chat
- `POST /api/bots/{id}/chat` - Chat với bot
- `GET /api/bots/{id}/conversations` - Lịch sử chat

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Rasa** - Chatbot engine
- **JWT** - Authentication

### Frontend
- **React 19** - UI library
- **Vite** - Build tool
- **Ant Design** - UI components
- **Axios** - HTTP client
- **React Router** - Routing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server (production)

## 📝 Tips & Tricks

### Training Data Best Practices

1. **Đa dạng câu hỏi**: Thêm nhiều cách hỏi khác nhau cho cùng một intent
2. **Intent rõ ràng**: Đặt tên intent có ý nghĩa (greeting, price_inquiry, etc.)
3. **Số lượng data**: Ít nhất 5-10 examples cho mỗi intent
4. **Ngôn ngữ nhất quán**: Sử dụng cùng ngôn ngữ trong toàn bộ training data

### Troubleshooting

**Bot không trả lời đúng?**
- Kiểm tra training data đã upload đúng chưa
- Đảm bảo bot đã train xong (status = ACTIVE)
- Thử retrain bot

**Training lâu quá?**
- Training thường mất 30-60 giây
- Kiểm tra logs: `docker logs chatbot_backend`

**Lỗi upload training data?**
- Kiểm tra format JSON đúng chưa
- Đảm bảo có đủ fields: user, bot, intent

## 🚀 Next Steps

- [ ] Add bot versioning
- [ ] Export/import bot configs
- [ ] A/B testing
- [ ] Webhook integrations
- [ ] Analytics dashboard với charts
- [ ] Multi-language support tốt hơn
- [ ] Rate limiting
- [ ] Unit tests

## 📞 Support

Nếu gặp vấn đề, check:
1. Docker logs: `docker-compose logs -f`
2. API docs: http://localhost:8000/docs
3. Browser console (F12)
