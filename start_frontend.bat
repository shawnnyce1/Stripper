@echo off
echo Starting Amazon Flex Grabber Frontend...

cd /d "%~dp0\frontend"

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Start the Expo development server without auth
echo Starting Expo development server...
npx expo start --offline

pause