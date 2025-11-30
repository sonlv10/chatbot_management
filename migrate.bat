@echo off
REM Script để chạy Alembic migrations trên Windows

setlocal enabledelayedexpansion

echo === Alembic Migration Manager ===
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check command
if "%1"=="" (
    goto :show_help
)

if /i "%1"=="upgrade" (
    echo Applying all pending migrations...
    alembic upgrade head
    if %errorlevel% equ 0 (
        echo.
        echo [32mMigrations applied successfully[0m
    ) else (
        echo.
        echo [31mError applying migrations[0m
        exit /b 1
    )
    goto :end
)

if /i "%1"=="downgrade" (
    echo Rolling back one migration...
    alembic downgrade -1
    if %errorlevel% equ 0 (
        echo.
        echo [32mRollback completed[0m
    ) else (
        echo.
        echo [31mError during rollback[0m
        exit /b 1
    )
    goto :end
)

if /i "%1"=="current" (
    echo Current migration version:
    alembic current
    goto :end
)

if /i "%1"=="history" (
    echo Migration history:
    alembic history --verbose
    goto :end
)

if /i "%1"=="create" (
    if "%2"=="" (
        echo [31mError: Migration name required[0m
        echo Usage: migrate.bat create ^<migration_name^>
        exit /b 1
    )
    echo Creating new migration: %2
    alembic revision -m "%2"
    if %errorlevel% equ 0 (
        echo.
        echo [32mMigration file created[0m
    )
    goto :end
)

if /i "%1"=="autogenerate" (
    if "%2"=="" (
        echo [31mError: Migration name required[0m
        echo Usage: migrate.bat autogenerate ^<migration_name^>
        exit /b 1
    )
    echo Auto-generating migration: %2
    alembic revision --autogenerate -m "%2"
    if %errorlevel% equ 0 (
        echo.
        echo [32mMigration file auto-generated[0m
        echo [33mPlease review the generated migration file before applying[0m
    )
    goto :end
)

if /i "%1"=="help" goto :show_help
if /i "%1"=="--help" goto :show_help
if /i "%1"=="-h" goto :show_help

echo [31mError: Unknown command '%1'[0m
echo.
goto :show_help

:show_help
echo Usage: migrate.bat [COMMAND]
echo.
echo Commands:
echo   upgrade         - Apply all pending migrations (alembic upgrade head)
echo   downgrade       - Rollback one migration (alembic downgrade -1)
echo   current         - Show current migration version
echo   history         - Show migration history
echo   create [name]   - Create a new migration file
echo   autogenerate [name] - Auto-generate migration from models
echo   help            - Show this help message
echo.
echo Examples:
echo   migrate.bat upgrade
echo   migrate.bat create add_user_avatar
echo   migrate.bat autogenerate add_new_fields
goto :end

:end
endlocal
