@echo off
echo ========================================
echo OpenAI Migration Script
echo ========================================
echo.

echo Step 1: Installing OpenAI dependencies...
pip install openai>=1.0.0 langchain-openai>=0.1.0
echo.

echo Step 2: Rebuilding FAISS index with OpenAI embeddings...
echo This will take a few minutes and requires internet connection...
python ingest.py
echo.

echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo You can now start the API server:
echo   python api_server.py
echo.
echo The server will use OpenAI instead of Ollama.
echo.
pause
