# Medical RAG API Documentation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_api.txt
```

### 2. Start Server
```bash
python api_server.py
```

Server will start on: `http://localhost:8000`

### 3. View API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

### 1. Health Check
**GET** `/health`

Check if API is running and pipeline is loaded.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "system": "Medical RAG - High-Risk Pregnancy Detection",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 2. Process Clinical Query
**POST** `/query`

Process a clinical query and get risk assessment.

**Request Body:**
```json
{
  "query": "38-year-old pregnant woman with BP 150/95, Hb 10.5, twin pregnancy",
  "care_level": "PHC",
  "verbose": false
}
```

**Parameters:**
- `query` (required): Clinical query string (min 10 characters)
- `care_level` (optional): Care level context - `ASHA`, `PHC`, `CHC`, or `DISTRICT` (default: `PHC`)
- `verbose` (optional): Include debug information (default: `false`)

**Response:**
```json
{
  "success": true,
  "query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
  "answer": "[CLINICAL DECISION SUPPORT — NOT A DIAGNOSIS]...",
  "blocked": false,
  "care_level": "PHC",
  "confidence": {
    "score": 0.75,
    "level": "MEDIUM",
    "original_score": 0.82,
    "ceiling_applied": ["weak_retrieval"],
    "breakdown": {
      "retrieval_quality": 0.80,
      "rule_coverage": 1.0,
      "chunk_agreement": 0.70,
      "extractor_confidence": 0.95
    }
  },
  "features": {
    "age": 38,
    "gestational_age_weeks": null,
    "systolic_bp": 150,
    "diastolic_bp": 95,
    "hemoglobin": 10.5,
    "fbs": null,
    "twin_pregnancy": true,
    "prior_cesarean": false,
    "placenta_previa": false,
    "comorbidities": [],
    "extraction_confidence": 0.95,
    "missing_fields": ["gestational_age", "glucose"]
  },
  "rule_output": {
    "overall_risk": "CRITICAL",
    "total_score": 10,
    "rule_coverage": 1.0,
    "triggered_rules": [
      "advanced_maternal_age",
      "hypertension",
      "mild_anemia",
      "twin_pregnancy"
    ],
    "risk_flags": [
      {
        "condition": "Advanced Maternal Age",
        "present": true,
        "severity": "major",
        "value": "38 years",
        "threshold": "≥35 years",
        "rationale": "Age ≥35 increases risk of chromosomal abnormalities, GDM, hypertension, cesarean delivery",
        "score": 3
      }
    ]
  },
  "retrieval_stats": {
    "rewritten_query": "Advanced maternal age pregnancy risk...",
    "faiss_count": 30,
    "bm25_count": 10,
    "final_count": 8,
    "retrieval_quality": 0.80,
    "chunk_agreement": 0.70
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "processing_time_ms": 8542.35
}
```

---

### 3. Get Care Levels
**GET** `/care-levels`

Get available care levels and their capabilities.

**Response:**
```json
{
  "care_levels": {
    "ASHA": {
      "name": "ASHA Worker / Community Level",
      "allowed_actions": ["recognize", "refer", "educate", "follow_up"],
      "forbidden_treatments": ["prescribe medication", "administer drugs", "perform procedures"]
    },
    "PHC": {
      "name": "Primary Health Center",
      "allowed_actions": ["stabilize", "refer", "basic_treatment", "monitoring"],
      "forbidden_treatments": ["specialist procedures", "advanced imaging", "intensive care"]
    },
    "CHC": {
      "name": "Community Health Center",
      "allowed_actions": ["treat", "stabilize", "refer_if_needed", "specialist_consult"],
      "forbidden_treatments": ["tertiary procedures", "nicu", "advanced surgery"]
    },
    "DISTRICT": {
      "name": "District Hospital / Tertiary Center",
      "allowed_actions": ["full_treatment", "specialist_care", "procedures", "icu"],
      "forbidden_treatments": []
    }
  }
}
```

---

### 4. Get System Info
**GET** `/system-info`

Get system capabilities and clinical rules.

**Response:**
```json
{
  "system": "Medical RAG - High-Risk Pregnancy Detection",
  "version": "1.0.0",
  "status": "production",
  "capabilities": {
    "feature_extraction": "Hybrid (Regex + LLM)",
    "retrieval": "FAISS + BM25 + RRF + Cross-encoder",
    "rule_engine": "12 clinical rules",
    "reasoning": "Evidence-grounded LLM",
    "hallucination_prevention": "Evidence attribution + Severity constraints",
    "confidence_scoring": "Weighted multi-component with ceilings",
    "care_level_awareness": "ASHA, PHC, CHC, District"
  },
  "clinical_rules": [
    "Advanced maternal age (≥35)",
    "Young maternal age (<20)",
    "Teenage pregnancy (<18)",
    "Severe anemia (Hb <7)",
    "Moderate anemia (Hb 7-10)",
    "Mild anemia (Hb 10-11)",
    "Severe hypertension (≥160/110)",
    "Hypertension (≥140/90)",
    "Overt diabetes (FBS ≥126)",
    "GDM (FBS ≥92)",
    "Twin pregnancy",
    "Previous cesarean",
    "Placenta previa"
  ],
  "safety_features": [
    "Evidence-gated validation (no hallucinations)",
    "Confidence ceilings (no overconfidence)",
    "Care-level filtering (appropriate recommendations)",
    "Severity constraint filters (no escalation)",
    "Topic isolation (condition-specific chunks)",
    "Drug completeness validation",
    "Steroid gating (appropriate timing)",
    "Internal consistency checks",
    "Citation validity",
    "Differential diagnosis clarity"
  ]
}
```

---

## 🧪 Testing

### Using Python Test Client
```bash
# Run full test suite
python test_api.py

# Test single query
python test_api.py "38-year-old with BP 150/95, Hb 10.5, twin pregnancy"
```

### Using cURL

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
    "care_level": "PHC",
    "verbose": false
  }'
```

### Using Python Requests
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
        "care_level": "PHC",
        "verbose": False
    }
)

data = response.json()
print(f"Risk: {data['rule_output']['overall_risk']}")
print(f"Score: {data['rule_output']['total_score']}")
print(f"Confidence: {data['confidence']['level']}")
```

---

## 📊 Response Fields Explained

### Confidence
- `score`: Overall confidence (0-1)
- `level`: Confidence label (`HIGH`, `MEDIUM`, `LOW`, `VERY_LOW`)
- `original_score`: Score before ceiling applied
- `ceiling_applied`: List of ceilings applied (e.g., `weak_retrieval`)
- `breakdown`: Component scores

### Features
- `age`: Patient age in years
- `gestational_age_weeks`: Gestational age
- `systolic_bp` / `diastolic_bp`: Blood pressure
- `hemoglobin`: Hemoglobin level (g/dL)
- `fbs`: Fasting blood sugar (mg/dL)
- `twin_pregnancy`: Boolean
- `prior_cesarean`: Boolean
- `placenta_previa`: Boolean
- `comorbidities`: List of conditions
- `extraction_confidence`: Feature extraction quality (0-1)
- `missing_fields`: List of fields not extracted

### Rule Output
- `overall_risk`: Risk level (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`)
- `total_score`: Numeric risk score
- `rule_coverage`: % of features with applicable rules (0-1)
- `triggered_rules`: List of triggered rule names
- `risk_flags`: Detailed risk flag information

### Retrieval Stats
- `rewritten_query`: Query after rewriting
- `faiss_count`: Chunks from FAISS
- `bm25_count`: Chunks from BM25
- `final_count`: Final chunks after reranking
- `retrieval_quality`: Quality score (0-1)
- `chunk_agreement`: Multi-chunk agreement (0-1)

---

## 🔒 Error Handling

### 400 Bad Request
Invalid input parameters.

**Example:**
```json
{
  "success": false,
  "error": "Invalid care_level. Must be one of: ASHA, PHC, CHC, DISTRICT",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 500 Internal Server Error
Server-side error during processing.

**Example:**
```json
{
  "success": false,
  "error": "Internal server error",
  "detail": "Error processing query: ...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 503 Service Unavailable
Pipeline not initialized.

**Example:**
```json
{
  "success": false,
  "error": "Pipeline not initialized",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🚀 Deployment

### Production Configuration

**1. Update CORS settings in `api_server.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**2. Disable reload:**
```python
uvicorn.run(
    "api_server:app",
    host="0.0.0.0",
    port=8000,
    reload=False,  # Production
    log_level="info"
)
```

**3. Use production ASGI server:**
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t medical-rag-api .
docker run -p 8000:8000 medical-rag-api
```

---

## 📈 Performance

### Typical Response Times
- Feature extraction: < 1 second
- Retrieval: 1-2 seconds
- LLM reasoning: 5-10 seconds
- Total: 6-13 seconds per query

### Optimization Tips
1. Use GPU for embeddings (if available)
2. Cache FAISS index in memory
3. Use connection pooling for Ollama
4. Enable response compression
5. Use async endpoints for concurrent requests

---

## 🔐 Security Considerations

### Production Checklist
- [ ] Enable HTTPS
- [ ] Add API key authentication
- [ ] Rate limiting
- [ ] Input validation
- [ ] Sanitize error messages
- [ ] Enable CORS only for trusted domains
- [ ] Log all requests
- [ ] Monitor for abuse
- [ ] Regular security audits

### Example: API Key Authentication
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/query")
async def process_query(
    request: QueryRequest,
    api_key: str = Security(verify_api_key)
):
    # ... process query
```

---

## 📚 Additional Resources

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **System Info:** `http://localhost:8000/system-info`
- **Care Levels:** `http://localhost:8000/care-levels`

---

## 🆘 Troubleshooting

### Issue: Pipeline not loading
**Solution:** Ensure Ollama is running and FAISS index exists
```bash
ollama serve
python main.py --ingest  # If index missing
```

### Issue: Slow responses
**Solution:** Check Ollama performance, consider GPU acceleration

### Issue: CORS errors
**Solution:** Update CORS settings in `api_server.py`

---

## 📞 Support

For issues or questions:
1. Check API documentation: `/docs`
2. Review system info: `/system-info`
3. Test with: `python test_api.py`

---

**API Version:** 1.0.0  
**System:** Medical RAG - High-Risk Pregnancy Detection  
**Status:** Production-Ready 🚀
