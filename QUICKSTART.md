# 🚀 Quick Start Guide

## Bước 1: Cài đặt

```bash
cd chatbot_management

# Copy environment file
cp backend/.env.example backend/.env
```

## Bước 2: Chạy hệ thống

```bash
# Start tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f
```

## Bước 3: Truy cập

- **API Backend**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Rasa**: http://localhost:5005

## 📝 Test API

### 1. Đăng ký user mới:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'
```

### 2. Login:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. Tạo bot (cần token):

```bash
TOKEN="your-access-token-here"

curl -X POST http://localhost:8000/api/bots/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Bot",
    "description": "Bot tư vấn sản phẩm",
    "language": "vi"
  }'
```

### 4. Upload training data:

```bash
# Tạo file training.json
cat > training.json << 'EOF'
[
  {
    "user": "Giá bao nhiêu?",
    "bot": "Sản phẩm này giá 299K ạ",
    "intent": "hoi_gia"
  },
  {
    "user": "Còn hàng không?",
    "bot": "Dạ còn hàng ạ",
    "intent": "hoi_hang"
  }
]
EOF

# Upload
curl -X POST http://localhost:8000/api/bots/1/training/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@training.json"
```

### 5. Lấy danh sách bots:

```bash
curl -X GET http://localhost:8000/api/bots/ \
  -H "Authorization: Bearer $TOKEN"
```

## 🛠️ Development

### Chạy backend riêng (không dùng Docker):

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload
```

### Database migration:

```bash
# Nếu thay đổi models, restart để tự động tạo tables
docker-compose restart backend
```

## 📊 Kiểm tra services:

```bash
# Check PostgreSQL
docker exec -it chatbot_postgres psql -U chatbot_user -d chatbot_db -c "SELECT * FROM users;"

# Check backend logs
docker-compose logs backend

# Check Rasa logs
docker-compose logs rasa
```

## 🔧 Troubleshooting

### Lỗi kết nối database:

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Xem logs
docker-compose logs postgres
```

### Lỗi import module:

```bash
# Rebuild backend
docker-compose build backend
docker-compose up -d backend
```

## 📝 Next Steps

1. ✅ Backend API hoạt động
2. ⏳ Tạo Frontend React
3. ⏳ Tích hợp Rasa training
4. ⏳ Test chat interface
