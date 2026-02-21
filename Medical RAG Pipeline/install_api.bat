@echo off
echo ========================================
echo FastAPI Dependencies Installation
echo ========================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Installing FastAPI and dependencies...
pip install -r requirements_api.txt
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the server, run:
echo   python api_server.py
echo.
echo Or press any key to start now...
pause

python api_server.py
