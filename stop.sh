#!/bin/bash

# ========================================
# Script Dung Ung Dung Chatbot
# ========================================

echo ""
echo "========================================"
echo "   DUNG CHATBOT MANAGEMENT SYSTEM"
echo "========================================"
echo ""

echo "Dang tim va dung cac process..."
echo ""

# Dung Backend (port 8000)
echo "[1/3] Dung Backend API..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    for pid in $(netstat -ano | grep :8000 | grep LISTENING | awk '{print $5}' | sort -u); do
        taskkill //PID $pid //F 2>/dev/null || true
    done
else
    # Linux/Mac
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

# Dung Rasa (port 5005)
echo "[2/3] Dung Rasa Server..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    for pid in $(netstat -ano | grep :5005 | grep LISTENING | awk '{print $5}' | sort -u); do
        taskkill //PID $pid //F 2>/dev/null || true
    done
else
    # Linux/Mac
    lsof -ti:5005 | xargs kill -9 2>/dev/null || true
fi

# Dung Frontend (port 5173)
echo "[3/3] Dung Frontend..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    for pid in $(netstat -ano | grep :5173 | grep LISTENING | awk '{print $5}' | sort -u); do
        taskkill //PID $pid //F 2>/dev/null || true
    done
    # Dung processes theo ten
    taskkill //IM node.exe //F 2>/dev/null || true
    taskkill //IM python.exe //F 2>/dev/null || true
else
    # Linux/Mac
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    # Dung processes theo ten
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "rasa run" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
fi

echo ""
echo "========================================"
echo "   TAT CA SERVICES DA DUNG"
echo "========================================"
echo ""
echo "Luu y: PostgreSQL van dang chay."
echo "De dung PostgreSQL:"
echo "  Windows: net stop postgresql-x64-14"
echo "  Linux: sudo systemctl stop postgresql"
echo "  Mac: brew services stop postgresql"
echo ""
