#!/bin/bash

echo "=== 1. Register User ==="
REGISTER=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"demo123","full_name":"Demo User"}')
echo "$REGISTER"

echo -e "\n=== 2. Login ==="
LOGIN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@test.com&password=demo123")
echo "$LOGIN"

TOKEN=$(echo "$LOGIN" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Token: ${TOKEN:0:50}..."

echo -e "\n=== 3. Create Bot ==="
BOT=$(curl -s -X POST http://localhost:8000/api/bots/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo English Bot","description":"Test bot with good training data","language":"en"}')
echo "$BOT"

BOT_ID=$(echo "$BOT" | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Bot ID: $BOT_ID"

echo -e "\n=== 4. Upload Training Data ==="
UPLOAD=$(curl -s -X POST http://localhost:8000/api/bots/$BOT_ID/training/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@demo_training.json")
echo "$UPLOAD"

echo -e "\n=== 5. Train Bot ==="
TRAIN=$(curl -s -X POST http://localhost:8000/api/bots/$BOT_ID/train \
  -H "Authorization: Bearer $TOKEN")
echo "$TRAIN"

echo -e "\n=== Wait for training (20s) ==="
sleep 20

echo -e "\n=== 6. Test Chat - hi ==="
CHAT1=$(curl -s -X POST http://localhost:8000/api/bots/$BOT_ID/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"hi"}')
echo "$CHAT1"

echo -e "\n=== 7. Test Chat - price ==="
CHAT2=$(curl -s -X POST http://localhost:8000/api/bots/$BOT_ID/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"how much"}')
echo "$CHAT2"

echo -e "\n=== 8. Test Chat - thanks ==="
CHAT3=$(curl -s -X POST http://localhost:8000/api/bots/$BOT_ID/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"thank you"}')
echo "$CHAT3"

echo -e "\n=== Complete! ==="
