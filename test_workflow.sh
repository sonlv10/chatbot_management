#!/bin/bash
# Test workflow: Register → Login → Create Bot → Upload Data → Train

echo "=== 1. Register User ==="
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@chatbot.com",
    "password": "test123",
    "full_name": "Test User"
  }')

echo "$REGISTER_RESPONSE" | python -m json.tool
echo ""

echo "=== 2. Login ==="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -F "username=test@chatbot.com" \
  -F "password=test123")

echo "$LOGIN_RESPONSE" | python -m json.tool

TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token: $TOKEN"
echo ""

echo "=== 3. Create Bot ==="
BOT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/bots/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Test Bot",
    "description": "Bot test tự động",
    "language": "vi"
  }')

echo "$BOT_RESPONSE" | python -m json.tool

BOT_ID=$(echo "$BOT_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Bot ID: $BOT_ID"
echo ""

echo "=== 4. Upload Training Data ==="
cat > /tmp/training_test.json << 'EOF'
[
  {
    "user": "Xin chào",
    "bot": "Xin chào! Tôi có thể giúp gì cho bạn?",
    "intent": "chao_hoi"
  },
  {
    "user": "Hello",
    "bot": "Xin chào! Tôi có thể giúp gì cho bạn?",
    "intent": "chao_hoi"
  },
  {
    "user": "Giá bao nhiêu?",
    "bot": "Sản phẩm này giá 299.000đ ạ",
    "intent": "hoi_gia"
  },
  {
    "user": "Bao tiền?",
    "bot": "Sản phẩm này giá 299.000đ ạ",
    "intent": "hoi_gia"
  },
  {
    "user": "Còn hàng không?",
    "bot": "Dạ còn hàng ạ, bạn muốn đặt hàng không?",
    "intent": "hoi_hang"
  },
  {
    "user": "Có sẵn không?",
    "bot": "Dạ còn hàng ạ, bạn muốn đặt hàng không?",
    "intent": "hoi_hang"
  },
  {
    "user": "Cảm ơn",
    "bot": "Không có gì, rất vui được hỗ trợ bạn!",
    "intent": "cam_on"
  },
  {
    "user": "Thanks",
    "bot": "Không có gì, rất vui được hỗ trợ bạn!",
    "intent": "cam_on"
  }
]
EOF

UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/bots/$BOT_ID/training/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/training_test.json")

echo "$UPLOAD_RESPONSE" | python -m json.tool
echo ""

echo "=== 5. Trigger Training ==="
TRAIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/bots/$BOT_ID/train" \
  -H "Authorization: Bearer $TOKEN")

echo "$TRAIN_RESPONSE" | python -m json.tool
echo ""

echo "=== 6. Check Training Status (wait 30s) ==="
sleep 30

STATUS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/bots/$BOT_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "$STATUS_RESPONSE" | python -m json.tool
echo ""

echo "=== 7. Test Chat ==="
CHAT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/bots/$BOT_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "sender_id": "test_user"}')

echo "$CHAT_RESPONSE" | python -m json.tool
echo ""

echo "=== 8. Test Another Message ==="
CHAT_RESPONSE2=$(curl -s -X POST "http://localhost:8000/api/bots/$BOT_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "How much?", "sender_id": "test_user"}')

echo "$CHAT_RESPONSE2" | python -m json.tool
echo ""

echo "=== Test Complete! ==="
echo "Bot ID: $BOT_ID"
echo "Token: $TOKEN"
