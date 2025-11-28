# Training Service API Guide

## 📚 **API Endpoints**

### 1. Upload Training Data
```bash
POST /api/bots/{bot_id}/training/upload
```

Upload JSON file với format:
```json
[
  {
    "user": "Câu hỏi của user",
    "bot": "Câu trả lời của bot",
    "intent": "ten_intent"
  }
]
```

### 2. Trigger Training
```bash
POST /api/bots/{bot_id}/train
```

Bắt đầu training model (chạy background).

### 3. Check Training Status
```bash
GET /api/bots/{bot_id}/training/sessions
```

Xem lịch sử training.

### 4. Chat with Bot
```bash
POST /api/bots/{bot_id}/chat
```

Body:
```json
{
  "message": "Xin chào",
  "sender_id": "user123"
}
```

### 5. Get Conversations
```bash
GET /api/bots/{bot_id}/conversations
```

## 🔄 **Workflow**

```
1. Register/Login
   ↓
2. Create Bot
   ↓
3. Upload Training Data (JSON)
   ↓
4. Trigger Training
   ↓
5. Wait for training (check status)
   ↓
6. Chat with bot
```

## 📝 **Training Data Format**

### Minimum 3 examples per intent:
```json
[
  {
    "user": "Giá bao nhiêu?",
    "bot": "299K ạ",
    "intent": "hoi_gia"
  },
  {
    "user": "Bao tiền?",
    "bot": "299K ạ",
    "intent": "hoi_gia"
  },
  {
    "user": "Hết bao nhiêu?",
    "bot": "299K ạ",
    "intent": "hoi_gia"
  }
]
```

## 🧪 **Test Script**

```bash
chmod +x test_workflow.sh
./test_workflow.sh
```

## 🎯 **Next Steps**

- [ ] Frontend UI for uploading training data
- [ ] Real-time training progress
- [ ] Model versioning
- [ ] A/B testing
