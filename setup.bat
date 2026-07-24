@echo off
cd /d "%~dp0"
echo =========================================================
echo   Smart Local Image Gallery - Google Photos Style
echo =========================================================
echo.

:: Check python version
python --version >nul 2>&1
if errorlevel 1 goto nopython

:: Create virtual environment if it does not exist
if exist .venv goto activate
echo [INFO] Creating Python virtual environment (.venv)...
python -m venv .venv
if errorlevel 1 goto venvfail

:activate
:: Activate virtual environment and install requirements
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 goto activatefail

echo [INFO] Installing/verifying package dependencies...
pip install -r requirements.txt
if errorlevel 1 goto pipfail

:: Start Flask Server
echo.
echo [INFO] Starting Flask Server...
echo [INFO] A browser window should open automatically to http://127.0.0.1:5000 in a few seconds.
echo [INFO] To stop the server, press Ctrl+C in this command window.
echo.

python app.py
if errorlevel 1 goto runfail
goto end

:nopython
echo [ERROR] Python is not installed or not in system PATH.
echo Please install Python 3.11 or later and check "Add Python to PATH".
goto end

:venvfail
echo [ERROR] Failed to create virtual environment.
goto end

:activatefail
echo [ERROR] Failed to activate virtual environment.
goto end

:pipfail
echo [ERROR] Failed to install pip dependencies.
goto end

:runfail
echo [WARNING] Server stopped or exited with error.
goto end

:end
pause
