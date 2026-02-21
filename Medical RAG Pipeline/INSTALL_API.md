# FastAPI Installation Guide

## Quick Install

### Option 1: Install All Dependencies (Recommended)

```bash
pip install -r requirements_api.txt
```

### Option 2: Install Only FastAPI Dependencies

If you already have the RAG dependencies installed:

```bash
pip install fastapi uvicorn[standard] pydantic python-multipart
```

---

## Detailed Installation Steps

### 1. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Upgrade pip

```bash
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
pip install -r requirements_api.txt
```

This will install:
- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type hints
- **python-multipart**: For handling file uploads (if needed)
- All RAG pipeline dependencies (LangChain, FAISS, etc.)

---

## Verify Installation

### Check FastAPI Installation

```bash
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
```

Expected output:
```
FastAPI version: 0.104.1 (or higher)
```

### Check Uvicorn Installation

```bash
python -c "import uvicorn; print('Uvicorn installed successfully')"
```

### Check All Dependencies

```bash
pip list | grep -E "fastapi|uvicorn|pydantic"
```

---

## Start the API Server

### Basic Start

```bash
python api_server.py
```

The server will start on: http://localhost:8000

### With Auto-Reload (Development)

```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Test the API

### 1. Check Health Endpoint

**Browser:**
```
http://localhost:8000/health
```

**cURL:**
```bash
curl http://localhost:8000/health
```

**PowerShell:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

### 2. Access API Documentation

**Swagger UI (Interactive):**
```
http://localhost:8000/docs
```

**ReDoc (Alternative):**
```
http://localhost:8000/redoc
```

### 3. Test Simplified Endpoint

```bash
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "query": "38-year-old with BP 155/98, Hb 6.2 at 32 weeks",
    "care_level": "PHC"
  }'
```

**PowerShell:**
```powershell
$body = @{
    query = "38-year-old with BP 155/98, Hb 6.2 at 32 weeks"
    care_level = "PHC"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/assess `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### 4. Run Test Script

```bash
python test_simple_api.py
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install fastapi uvicorn
```

### Issue: "ModuleNotFoundError: No module named 'pydantic'"

**Solution:**
```bash
pip install pydantic
```

### Issue: Port 8000 already in use

**Solution 1: Use different port**
```bash
uvicorn api_server:app --port 8001
```

**Solution 2: Kill process on port 8000**

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Issue: "ImportError: cannot import name 'ProductionRAGPipeline'"

**Solution:** Make sure you're in the correct directory with all pipeline files:
```bash
ls production_pipeline.py  # Should exist
python api_server.py
```

### Issue: Slow startup (loading models)

This is normal. The server loads:
- Cross-encoder model (~200MB)
- FAISS index
- LangChain components

First startup takes 30-60 seconds. Subsequent requests are fast.

---

## Dependencies Breakdown

### Core FastAPI Stack
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation
- `python-multipart`: File upload support

### RAG Pipeline Stack
- `langchain`: LLM framework
- `langchain-community`: Community integrations
- `langchain-ollama`: Ollama integration
- `faiss-cpu`: Vector similarity search
- `sentence-transformers`: Embeddings
- `rank-bm25`: BM25 retrieval
- `torch`: PyTorch for models
- `transformers`: Hugging Face models

### Utilities
- `requests`: HTTP client
- `numpy`: Numerical computing
- `tqdm`: Progress bars
- `PyMuPDF`: PDF processing

---

## System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 2GB disk space

### Recommended
- Python 3.10+
- 8GB RAM
- 5GB disk space (for models)
- Ollama installed with mistral:7b-instruct model

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Start API server
3. ✅ Test health endpoint
4. ✅ Try simplified /assess endpoint
5. 📖 Read SIMPLE_API_GUIDE.md for usage examples
6. 🧪 Run test suite: `python test_simple_api.py`

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pip install -r requirements_api.txt` | Install all dependencies |
| `python api_server.py` | Start server |
| `curl http://localhost:8000/health` | Check server health |
| `python test_simple_api.py` | Run tests |

---

*Last Updated: 2026-02-20*
