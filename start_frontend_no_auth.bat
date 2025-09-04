@echo off
echo Starting Amazon Flex Grabber Frontend (No Auth)...

cd /d "%~dp0\frontend"

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Start without authentication
echo Starting Expo development server without auth...
npx expo start --offline

pause