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

# Kiem tra PostgreSQL
echo "[1/5] Kiem tra PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL chua chay. Vui long khoi dong PostgreSQL truoc:"
    echo "  Windows: net start postgresql-x64-14"
    echo "  Linux/Mac: sudo systemctl start postgresql"
    exit 1
fi
echo "PostgreSQL da chay."

# Kiem tra database
echo ""
echo "[2/5] Kiem tra database..."
if ! psql -U chatbot_user -d chatbot_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Database chua ton tai. Vui long chay setup truoc!"
    echo "Chi tiet: xem file SETUP_WITHOUT_DOCKER.md"
    exit 1
fi
echo "Database OK."

# Khoi dong Backend
echo ""
echo "[3/5] Khoi dong Backend API..."
cd "$SCRIPT_DIR/backend"

# Detect OS and open appropriate terminal
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    cmd.exe /c start "Chatbot Backend" bash -c "cd '$SCRIPT_DIR/backend' && source venv/Scripts/activate && echo 'Backend dang khoi dong...' && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; exec bash"
else
    # Linux/Mac
    source venv/bin/activate
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend' && source venv/bin/activate && echo 'Backend dang khoi dong...' && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; exec bash" 2>/dev/null || \
    xterm -e "cd '$SCRIPT_DIR/backend' && source venv/bin/activate && echo 'Backend dang khoi dong...' && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; bash" &
fi
sleep 3

# Khoi dong Rasa
echo ""
echo "[4/5] Khoi dong Rasa Server..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    cmd.exe /c start "Chatbot Rasa" bash -c "cd '$SCRIPT_DIR/backend' && source venv/Scripts/activate && echo 'Rasa dang khoi dong...' && rasa run --enable-api --cors '*' --port 5005; exec bash"
else
    # Linux/Mac
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend' && source venv/bin/activate && echo 'Rasa dang khoi dong...' && rasa run --enable-api --cors '*' --port 5005; exec bash" 2>/dev/null || \
    xterm -e "cd '$SCRIPT_DIR/backend' && source venv/bin/activate && echo 'Rasa dang khoi dong...' && rasa run --enable-api --cors '*' --port 5005; bash" &
fi
sleep 5

# Khoi dong Frontend
echo ""
echo "[5/5] Khoi dong Frontend..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    cmd.exe /c start "Chatbot Frontend" bash -c "cd '$SCRIPT_DIR/frontend' && echo 'Frontend dang khoi dong...' && npm run dev; exec bash"
else
    # Linux/Mac
    gnome-terminal -- bash -c "cd '$SCRIPT_DIR/frontend' && echo 'Frontend dang khoi dong...' && npm run dev; exec bash" 2>/dev/null || \
    xterm -e "cd '$SCRIPT_DIR/frontend' && echo 'Frontend dang khoi dong...' && npm run dev; bash" &
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
echo "Cac service dang chay trong cac terminal rieng."
echo ""
