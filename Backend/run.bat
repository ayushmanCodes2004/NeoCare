@echo off
echo ========================================
echo ANC Service - Spring Boot Backend
echo ========================================
echo.

echo Checking Java version...
java -version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 17 or higher
    pause
    exit /b 1
)

echo.
echo Building project...
call mvn clean install -DskipTests
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo Starting Spring Boot application...
echo Server will start on http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.
call mvn spring-boot:run
