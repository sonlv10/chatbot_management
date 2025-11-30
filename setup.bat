@echo off
REM ====================================
REM Chatbot Management Setup Script
REM For Windows (Without Docker)
REM ====================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Chatbot Management Setup
echo   (Local Development Environment)
echo ========================================
echo.

REM Check if Python is installed
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python is not installed or not in PATH
    echo.
    set /p install_python="Do you want to download and install Python 3.10? (Y/N): "
    if /i "!install_python!"=="Y" (
        echo.
        echo Downloading Python 3.10.13...
        echo Please wait, this may take a few minutes...
        
        REM Download Python installer
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.13/python-3.10.13-amd64.exe' -OutFile '%TEMP%\python-installer.exe'}"
        
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to download Python installer
            echo Please download manually from: https://www.python.org/downloads/
            pause
            exit /b 1
        )
        
        echo.
        echo Installing Python 3.10.11...
        echo IMPORTANT: The installer will open. Please check:
        echo   [X] Add Python to PATH
        echo   [X] Install for all users (optional)
        echo.
        echo Press any key to start installation...
        pause >nul
        
        REM Run installer with options
        start /wait %TEMP%\python-installer.exe /passive InstallAllUsers=1 PrependPath=1 Include_test=0
        
        REM Clean up
        del %TEMP%\python-installer.exe
        
        echo.
        echo Python installation completed!
        echo Please close this window and run setup.bat again.
        pause
        exit /b 0
    ) else (
        echo.
        echo [ERROR] Python is required to continue
        echo Please install Python 3.10+ from: https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
)
echo [OK] Python is installed
python --version
echo.

REM Check if Node.js is installed
echo [2/8] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Node.js is not installed or not in PATH
    echo.
    set /p install_node="Do you want to download and install Node.js 20 LTS? (Y/N): "
    if /i "!install_node!"=="Y" (
        echo.
        echo Downloading Node.js 20.11.0 LTS...
        echo Please wait, this may take a few minutes...
        
        REM Download Node.js installer
REM Check if PostgreSQL is installed
echo [3/8] Checking PostgreSQL installation...
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL is not in PATH
    echo.
    set /p install_postgres="Do you want to download and install PostgreSQL 16? (Y/N): "
    if /i "!install_postgres!"=="Y" (
        echo.
        echo Downloading PostgreSQL 14.10...
        echo Please wait, this may take several minutes (file size ~250MB)...
        
        REM Download PostgreSQL installer
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://get.enterprisedb.com/postgresql/postgresql-14.10-1-windows-x64.exe' -OutFile '%TEMP%\postgresql-installer.exe'}"
        
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to download PostgreSQL installer
            echo Please download manually from: https://www.postgresql.org/download/windows/
            pause
            exit /b 1
        )
        
        echo.
        echo Installing PostgreSQL 14.10...
        echo.
        echo IMPORTANT: During installation, please:
        echo   1. Remember the password you set for 'postgres' user
        echo   2. Keep default port: 5432
        echo   3. Select components: PostgreSQL Server, pgAdmin 4, Command Line Tools
        echo.
        echo Press any key to start installation...
        pause >nul
        
        REM Run installer (interactive mode required for password setup)
        start /wait %TEMP%\postgresql-installer.exe --mode unattended --superpassword postgres --serverport 5432
        
        REM Clean up
        del %TEMP%\postgresql-installer.exe
        
        echo.
        echo PostgreSQL 14.10 installation completed!
        echo Default superuser: postgres
        echo Default password: postgres (change it after installation!)
        echo.
        echo Please close this window and run setup.bat again.
        pause
        exit /b 0
    ) else (
        echo.
        echo [WARNING] PostgreSQL is recommended but not required for setup
        echo You can install it manually later from: https://www.postgresql.org/download/windows/
        echo.
        set /p continue_without_pg="Continue without PostgreSQL? (Y/N): "
        if /i not "!continue_without_pg!"=="Y" exit /b 1
    )
) else (
    echo [OK] PostgreSQL is installed
    psql --version
)
echo.   REM Run installer
        start /wait msiexec /i %TEMP%\node-installer.msi /passive
        
        REM Clean up
        del %TEMP%\node-installer.msi
        
        echo.
        echo Node.js 20.11.0 LTS installation completed!
        echo Please close this window and run setup.bat again.
        pause
        exit /b 0
    ) else (
        echo.
        echo [ERROR] Node.js is required to continue
        echo Please install Node.js 18+ from: https://nodejs.org/
        pause
        exit /b 1
    )
)
echo [OK] Node.js is installed
node --version
echo.

REM Check if PostgreSQL is installed
echo [3/8] Checking PostgreSQL installation...
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL is not in PATH
    echo Please make sure PostgreSQL 14+ is installed and running
    echo Download from: https://www.postgresql.org/download/windows/
    echo.
    echo If already installed, you need to add it to PATH or continue manually
    set /p continue="Continue anyway? (Y/N): "
    if /i not "!continue!"=="Y" exit /b 1
) else (
    echo [OK] PostgreSQL is installed
    psql --version
)
echo.

REM Setup Backend
echo [4/8] Setting up Backend (Python virtual environment)...
cd /d "%~dp0backend"

if exist venv (
    echo Virtual environment already exists, skipping creation...
) else (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed

REM Create .env file if not exists
if not exist .env (
    echo Creating .env file...
    (
        echo # Database
        echo DATABASE_URL=postgresql://chatbot_user:chatbot_pass@localhost:5432/chatbot_db
        echo.
        echo # Security
        echo SECRET_KEY=your-secret-key-change-this-in-production-123456789
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo.
        echo # Rasa
        echo RASA_SERVER_URL=http://localhost:5005
    ) > .env
    echo [OK] Created .env file
)

cd /d "%~dp0"
echo.

REM ============================================
REM 5. Setup Database
REM ============================================
echo [5/8] Setting up Database...

REM Check if PostgreSQL service is running
sc query postgresql-x64-14 | find "RUNNING" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] PostgreSQL service not running, attempting to start...
    net start postgresql-x64-14 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Could not start PostgreSQL service automatically
        echo Please start PostgreSQL manually and press any key to continue...
        pause >nul
    ) else (
        echo [OK] PostgreSQL service started
        timeout /t 3 >nul
    )
)

cd /d "%~dp0"
echo.

REM Check if database exists
psql -U postgres -lqt 2>nul | findstr /C:"chatbot_db" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Database 'chatbot_db' already exists
) else (
    echo Database not found. Creating database and user...
    
    REM Try to create database with default password
    psql -U postgres -c "CREATE USER chatbot_user WITH PASSWORD 'chatbot_pass';" 2>nul
    psql -U postgres -c "CREATE DATABASE chatbot_db OWNER chatbot_user;" 2>nul
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;" 2>nul
    
    REM Verify creation
    psql -U postgres -lqt 2>nul | findstr /C:"chatbot_db" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Database created successfully
    ) else (
        echo.
        echo [WARNING] Automatic database creation failed
        echo This usually means the postgres password is not 'postgres'
        echo.
        echo Please run these commands manually in psql or pgAdmin:
        echo   CREATE USER chatbot_user WITH PASSWORD 'chatbot_pass';
        echo   CREATE DATABASE chatbot_db OWNER chatbot_user;
        echo   GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
        echo.
        set /p db_ready="Press Y when database is ready (or N to exit): "
        if /i not "!db_ready!"=="Y" (
            set PGPASSWORD=
            exit /b 1
        )
    )
)

REM Clear password variable
set PGPASSWORD=
echo.

REM Setup Frontend
echo [6/8] Setting up Frontend (Node.js dependencies)...
cd /d "%~dp0frontend"

echo Installing npm dependencies...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install npm dependencies
    pause
    exit /b 1
)
echo [OK] Frontend dependencies installed

REM Create .env file if not exists
if not exist .env (
    echo Creating .env file...
    echo VITE_API_URL=http://localhost:8000/api > .env
    echo [OK] Created .env file
)

cd /d "%~dp0"
echo.

REM Setup Rasa
echo [7/8] Setting up Rasa Server...
cd /d "%~dp0rasa"

if exist venv_rasa (
    echo Rasa virtual environment already exists, skipping creation...
) else (
    echo Creating Rasa virtual environment...
    python -m venv venv_rasa
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create Rasa virtual environment
        pause
        exit /b 1
    )
)

echo Activating Rasa virtual environment...
call venv_rasa\Scripts\activate.bat

echo Installing Rasa...
pip install rasa==3.6.20
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install Rasa
    echo You can install it manually later with: pip install rasa
)

cd /d "%~dp0"
echo.

REM ============================================
REM 8. Run Database Migrations
REM ============================================
echo [8/8] Running Database Migrations...
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
alembic upgrade head
if %errorlevel% neq 0 (
    echo [WARNING] Failed to run migrations
    echo You can run migrations manually later with: migrate.bat upgrade
) else (
    echo [OK] Database migrations completed
)
cd /d "%~dp0"
echo.

REM Final instructions
echo ========================================
echo   Setup completed!
echo ========================================
echo.
echo Virtual environments created:
echo   - Backend:  backend\venv
echo   - Rasa:     rasa\venv_rasa
echo.
echo Configuration files created:
echo   - backend\.env
echo   - frontend\.env
echo.
echo Next steps:
echo   1. Make sure PostgreSQL is running
echo   2. If not done, create database manually (see above)
echo   3. Run migrations: migrate.bat upgrade
echo   4. Start services with: start.bat
echo.
echo Or start services manually:
echo   Terminal 1: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo   Terminal 2: cd rasa ^&^& venv_rasa\Scripts\activate ^&^& rasa run --enable-api --cors "*"
echo   Terminal 3: cd frontend ^&^& npm run dev
echo.
echo Default login:
echo   Email: demo@chatbot.com
echo   Password: demo123
echo.
echo For detailed setup guide, see: SETUP_WITHOUT_DOCKER.md
echo.
pause
