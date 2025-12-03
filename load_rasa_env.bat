@echo off
REM Helper script to load .env file for Rasa

if exist "%~dp0rasa\.env" (
    for /f "usebackq tokens=*" %%a in ("%~dp0rasa\.env") do (
        set line=%%a
        REM Skip comments and empty lines
        echo !line! | findstr /r "^#" >nul
        if errorlevel 1 (
            echo !line! | findstr /r "^$" >nul
            if errorlevel 1 (
                set %%a
            )
        )
    )
)
