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
echo [1/3] Kiem tra PostgreSQL...
sc query postgresql-x64-14 | find "RUNNING" >nul
if %errorlevel% neq 0 (
    echo PostgreSQL chua chay. Dang khoi dong...
    net start postgresql-x64-14
    timeout /t 3 >nul
) else (
    echo PostgreSQL da chay.
)

REM Tao thu muc logs neu chua co
if not exist "logs" mkdir logs

REM Khoi dong Backend
echo.
echo [2/3] Khoi dong Backend API...
cd /d %~dp0backend
call venv\Scripts\activate
start /B cmd /c "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ..\logs\backend.log 2>&1"
cd ..
timeout /t 3 >nul

REM Khoi dong Rasa
echo.
echo [3/3] Khoi dong Rasa Server...

REM Load environment variables from .env file
if exist "%~dp0rasa\.env" (
    for /f "usebackq tokens=* delims=" %%a in ("%~dp0rasa\.env") do (
        echo %%a | findstr /r "^[^#]" >nul
        if not errorlevel 1 (
            set %%a
        )
    )
)

REM Activate venv and run Rasa from rasa directory
cd /d %~dp0
call backend\venv\Scripts\activate

REM Find the latest model directory (bot folder)
set LATEST_BOT_DIR=
for /f "delims=" %%a in ('powershell -Command "Get-ChildItem -Path 'rasa\models\bot_*' -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty Name"') do set LATEST_BOT_DIR=%%a

REM Change to rasa directory and run
cd /d %~dp0rasa
if defined LATEST_BOT_DIR (
    echo Dang su dung models trong: models\%LATEST_BOT_DIR%
    start /B cmd /c "rasa run --enable-api --cors * --port 5005 --endpoints endpoints.yml --model models\%LATEST_BOT_DIR% > ..\logs\rasa.log 2>&1"
) else (
    echo Khong tim thay bot nao, khoi dong Rasa voi thu muc models mac dinh
    start /B cmd /c "rasa run --enable-api --cors * --port 5005 --endpoints endpoints.yml --model models > ..\logs\rasa.log 2>&1"
)
cd /d %~dp0
timeout /t 5 >nul

REM Khoi dong Frontend
echo.
echo [4/4] Khoi dong Frontend...
cd /d %~dp0frontend
start /B cmd /c "npm run dev > ..\logs\frontend.log 2>&1"
cd ..
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
echo Logs duoc luu trong thu muc: logs\
echo   - backend.log
echo   - rasa.log
echo   - frontend.log
echo.
echo De xem logs real-time, mo file logs hoac dung:
echo   Get-Content logs\backend.log -Wait    (PowerShell)
echo   type logs\backend.log                 (CMD)
echo.
echo De dung tat ca services, chay: stop.bat
echo.
echo Nhan phim bat ky de dong cua so nay...
echo Cac service se tiep tuc chay trong background.
echo.
pause
