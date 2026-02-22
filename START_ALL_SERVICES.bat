@echo off
echo ========================================
echo   NeoSure - Starting All Services
echo ========================================
echo.

echo [1/3] Starting Backend on port 8080...
start "NeoSure Backend" cmd /k "cd Backend && mvn spring-boot:run"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Medical RAG Pipeline on port 8000...
start "Medical RAG Pipeline" cmd /k "cd Medical RAG Pipeline && python api_server.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Lovable Frontend on port 5173...
start "Lovable Frontend" cmd /k "cd Frontend\lovable-frontend && npm run dev"

echo.
echo ========================================
echo   All Services Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8080
echo RAG API:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Swagger:  http://localhost:8080/swagger-ui/index.html
echo API Test: http://localhost:8080/api-tester.html
echo.
echo Press any key to exit...
pause >nul
