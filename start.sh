#!/bin/bash

# ========================================
# Script Khoi Dong Ung Dung Chatbot
# ========================================

echo ""
echo "========================================"
echo "   CHATBOT MANAGEMENT SYSTEM"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Kiem tra PostgreSQL
echo "[1/3] Kiem tra PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL chua chay. Vui long khoi dong PostgreSQL truoc:"
    echo "  Windows: net start postgresql-x64-14"
    echo "  Linux/Mac: sudo systemctl start postgresql"
    exit 1
fi
echo "PostgreSQL da chay."

# Khoi dong Backend
echo ""
echo "[2/3] Khoi dong Backend API..."
cd "$SCRIPT_DIR/backend"

# Detect OS and open appropriate terminal
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash) - Background mode with logs
    source venv/Scripts/activate
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
    echo "Backend PID: $!"
else
    # Linux/Mac
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
    echo "Backend PID: $!"
fi
sleep 3

# Khoi dong Rasa
echo ""
echo "[3/3] Khoi dong Rasa Server..."

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/rasa/.env" ]; then
    export $(cat "$SCRIPT_DIR/rasa/.env" | grep -v '^#' | xargs)
fi

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash) - Background mode with logs
    cd "$SCRIPT_DIR/backend"
    source venv/Scripts/activate
    nohup rasa run --enable-api --cors '*' --port 5005 > "$SCRIPT_DIR/logs/rasa.log" 2>&1 &
    echo "Rasa PID: $!"
else
    # Linux/Mac
    cd "$SCRIPT_DIR/backend"
    source venv/bin/activate
    nohup rasa run --enable-api --cors '*' --port 5005 > "$SCRIPT_DIR/logs/rasa.log" 2>&1 &
    echo "Rasa PID: $!"
fi
sleep 5

# Khoi dong Frontend
echo ""
echo "[4/4] Khoi dong Frontend..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash) - Background mode with logs
    cd "$SCRIPT_DIR/frontend"
    nohup npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    echo "Frontend PID: $!"
else
    # Linux/Mac
    cd "$SCRIPT_DIR/frontend"
    nohup npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    echo "Frontend PID: $!"
fi
sleep 3

echo ""
echo "========================================"
echo "   TAT CA SERVICES DA KHOI DONG"
echo "========================================"
echo ""
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Rasa Server:  http://localhost:5005"
echo "Frontend:     http://localhost:5173"
echo ""
echo "Logs duoc luu trong thu muc: logs/"
echo "  - backend.log"
echo "  - rasa.log"
echo "  - frontend.log"
echo ""
echo "De xem logs real-time, dung lenh:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/rasa.log"
echo "  tail -f logs/frontend.log"
echo ""
echo "De dung tat ca services, chay: bash stop.sh"
echo ""
echo "Cac service dang chay trong background."
echo ""
