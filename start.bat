@echo off
REM ========================================
REM Script Khoi Dong Ung Dung Chatbot
REM ========================================

echo.
echo ========================================
echo   CHATBOT MANAGEMENT SYSTEM
echo ========================================
echo.

REM Kiem tra PostgreSQL service
echo [1/5] Kiem tra PostgreSQL...
sc query postgresql-x64-14 | find "RUNNING" >nul
if %errorlevel% neq 0 (
    echo PostgreSQL chua chay. Dang khoi dong...
    net start postgresql-x64-14
    timeout /t 3 >nul
) else (
    echo PostgreSQL da chay.
)

REM Kiem tra database
echo.
echo [2/5] Kiem tra database...
psql -U chatbot_user -d chatbot_db -c "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    echo Database chua ton tai. Vui long chay setup truoc!
    echo Chi tiet: xem file SETUP_WITHOUT_DOCKER.md
    pause
    exit /b 1
)
echo Database OK.

REM Khoi dong Backend
echo.
echo [3/5] Khoi dong Backend API...
start "Chatbot Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && echo Backend dang khoi dong... && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 >nul

REM Khoi dong Rasa
echo.
echo [4/5] Khoi dong Rasa Server...
start "Chatbot Rasa" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && echo Rasa dang khoi dong... && rasa run --enable-api --cors * --port 5005"
timeout /t 5 >nul

REM Khoi dong Frontend
echo.
echo [5/5] Khoi dong Frontend...
start "Chatbot Frontend" cmd /k "cd /d %~dp0frontend && echo Frontend dang khoi dong... && npm run dev"
timeout /t 3 >nul

echo.
echo ========================================
echo   TAT CA SERVICES DA KHOI DONG
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Rasa Server:  http://localhost:5005
echo Frontend:     http://localhost:5173
echo.
echo Nhan phim bat ky de dong cua so nay...
echo Cac service se tiep tuc chay trong cac cua so rieng.
echo.
pause
