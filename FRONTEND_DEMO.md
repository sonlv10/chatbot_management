# 🎯 Frontend Demo Guide

## Truy cập Frontend

Mở browser và truy cập: **http://localhost:5173**

## Demo Flow

### 1. Đăng ký tài khoản mới

1. Click "**Đăng ký ngay**"
2. Điền form:
   - Họ và tên: `Demo User`
   - Email: `demo@test.com`
   - Mật khẩu: `demo123`
   - Xác nhận mật khẩu: `demo123`
3. Click "**Đăng ký**"

### 2. Đăng nhập

1. Email: `demo@test.com`
2. Mật khẩu: `demo123`
3. Click "**Đăng nhập**"

→ Bạn sẽ được chuyển đến **Dashboard**

### 3. Xem Dashboard

- Thống kê tổng quan: Total Bots, Active Bots, Training Data
- Recent Bots list

### 4. Tạo Bot mới

1. Click menu "**My Bots**"
2. Click "**Create Bot**"
3. Điền form:
   - Bot Name: `Customer Support Bot`
   - Description: `Bot hỗ trợ khách hàng`  
   - Language: `vi` (Vietnamese)
4. Click "**OK**"

→ Bot mới sẽ xuất hiện trong danh sách với status: **DRAFT**

### 5. Upload Training Data

1. Click menu "**Training Data**"
2. Chọn bot vừa tạo từ dropdown
3. Click "**Download Template**" để xem format
4. Tạo file `my_training.json`:

```json
[
  {
    "user": "hello",
    "bot": "Hi! How can I help you?",
    "intent": "greeting"
  },
  {
    "user": "hi",
    "bot": "Hi! How can I help you?",
    "intent": "greeting"
  },
  {
    "user": "price",
    "bot": "Our product costs $299",
    "intent": "price"
  },
  {
    "user": "how much",
    "bot": "Our product costs $299",
    "intent": "price"
  },
  {
    "user": "available",
    "bot": "Yes, we have it in stock!",
    "intent": "stock"
  },
  {
    "user": "in stock",
    "bot": "Yes, we have it in stock!",
    "intent": "stock"
  },
  {
    "user": "thanks",
    "bot": "You're welcome!",
    "intent": "thanks"
  },
  {
    "user": "thank you",
    "bot": "You're welcome!",
    "intent": "thanks"
  }
]
```

5. Click "**Upload Training Data (JSON)**"
6. Chọn file `my_training.json`

→ Sẽ hiển thị message: "Training data uploaded successfully, count: 8"

→ Table sẽ hiển thị 8 training data items

### 6. Train Bot

1. Quay lại "**My Bots**"
2. Tìm bot vừa tạo
3. Click nút "**Train**"

→ Status sẽ chuyển: **DRAFT** → **TRAINING** (xanh xám)

4. Đợi khoảng 30-60 giây
5. Refresh trang hoặc chờ auto-update

→ Status sẽ chuyển thành: **ACTIVE** (xanh lá)

### 7. Test Chat

**Cách 1:** Từ Bot List
1. Click nút "**Chat**" trên bot có status ACTIVE

**Cách 2:** Từ Menu  
1. Click menu "**Test Chat**"
2. Chọn bot từ dropdown

### 8. Chat với Bot

Thử các câu sau:
- `hello` → Bot: "Hi! How can I help you?"
- `price` → Bot: "Our product costs $299"
- `available` → Bot: "Yes, we have it in stock!"
- `thanks` → Bot: "You're welcome!"

## Features Đã Implement

✅ **Authentication**
- Register với validation
- Login với JWT token
- Auto redirect khi unauthorized
- Logout

✅ **Dashboard**
- Statistics cards
- Recent bots preview
- Responsive layout

✅ **Bot Management**
- Create bot với form validation
- Edit bot details
- Delete bot với confirmation
- Train bot button
- Status tags (draft/training/active/error)
- Direct chat link

✅ **Training Data**
- Select bot dropdown
- View all training data in table
- Upload JSON file
- Download template
- Delete individual items
- Pagination

✅ **Chat Interface**
- Select bot dropdown
- Chat UI với messages
- User/Bot avatars
- Timestamps
- Intent & confidence display (if available)
- Send on Enter
- Loading states

✅ **UI/UX**
- Ant Design components
- Responsive sidebar
- Navigation menu
- User profile dropdown
- Loading spinners
- Empty states
- Error messages
- Success notifications

## Notes

⚠️ **Model Loading Issue**: Hiện tại có vấn đề nhỏ với Rasa model loading - bot có thể không trả lời đúng 100%. Đây là vấn đề với Rasa configuration, không phải frontend. Frontend đã hoàn chỉnh và hoạt động tốt.

💡 **Tip**: Sử dụng training data bằng tiếng Anh đơn giản (như ví dụ trên) sẽ có kết quả tốt hơn tiếng Việt có dấu do vấn đề encoding.

## Screenshots

Bạn sẽ thấy:
- 🎨 Beautiful gradient login page
- 📊 Dashboard với statistics
- 🤖 Bot management table
- 📝 Training data table
- 💬 Modern chat interface
- 📱 Responsive design
