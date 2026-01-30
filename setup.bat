@echo off
REM Wiki Quiz Hub - Local Development Setup Script (Windows)
REM This script sets up the backend for local development

echo.
echo 🚀 Wiki Quiz Hub - Local Setup
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+
    echo Download from: https://www.python.org/downloads/
    exit /b 1
)

echo ✅ Python found

REM Navigate to backend
cd backend
if errorlevel 1 (
    echo ❌ backend folder not found
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Copy .env file
if not exist .env (
    echo ⚙️ Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env with your configuration
)

REM Initialize database
echo 🗄️ Initializing database...
python seed_database.py

echo.
echo ✅ Setup complete!
echo.
echo To start the development server, run:
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo Then visit: http://localhost:8000/docs
pause
