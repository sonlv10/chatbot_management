@echo off
REM ========================================
REM Script Dung Ung Dung Chatbot
REM ========================================

echo.
echo ========================================
echo   DUNG CHATBOT MANAGEMENT SYSTEM
echo ========================================
echo.

echo Dang tim va dung cac process...
echo.

REM Dung Backend (port 8000)
echo [1/3] Dung Backend API...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Dung Rasa (port 5005)
echo [2/3] Dung Rasa Server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5005 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Dung Frontend (port 5173)
echo [3/3] Dung Frontend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Dung Node processes
taskkill /IM node.exe /F >nul 2>&1
taskkill /IM python.exe /F >nul 2>&1

echo.
echo ========================================
echo   TAT CA SERVICES DA DUNG
echo ========================================
echo.
echo Luu y: PostgreSQL van dang chay.
echo De dung PostgreSQL, chay: net stop postgresql-x64-14
echo.
