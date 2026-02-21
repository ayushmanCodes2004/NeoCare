# FastAPI Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements_api.txt
```

### Step 2: Start the Server
```bash
python api_server.py
```

You should see:
```
🏥 Medical RAG API Server
======================================================================
Starting server on http://localhost:8000
API Documentation: http://localhost:8000/docs
======================================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test the API
```bash
python test_api.py
```

---

## 📡 Quick API Examples

### Example 1: Health Check
```bash
curl http://localhost:8000/health
```

### Example 2: Simple Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy"
  }'
```

### Example 3: Python Client
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy"}
)

data = response.json()
print(f"Risk: {data['rule_output']['overall_risk']}")
print(f"Confidence: {data['confidence']['level']}")
```

---

## 🎯 Common Use Cases

### Use Case 1: High-Risk Screening
```python
import requests

def screen_patient(age, bp_systolic, bp_diastolic, hemoglobin, **kwargs):
    query = f"{age}-year-old with BP {bp_systolic}/{bp_diastolic}, Hb {hemoglobin}"
    
    if kwargs.get('twin_pregnancy'):
        query += ", twin pregnancy"
    if kwargs.get('prior_cesarean'):
        query += ", previous cesarean"
    
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query, "care_level": "PHC"}
    )
    
    return response.json()

# Example
result = screen_patient(
    age=38,
    bp_systolic=150,
    bp_diastolic=95,
    hemoglobin=10.5,
    twin_pregnancy=True
)

print(f"Risk Level: {result['rule_output']['overall_risk']}")
print(f"Risk Score: {result['rule_output']['total_score']}")
```

### Use Case 2: Batch Processing
```python
import requests

patients = [
    "38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
    "28-year-old with Hb 10.5",
    "19-year-old at 8 weeks with Hb 7.5, BP 145/95",
]

results = []
for query in patients:
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query}
    )
    results.append(response.json())

# Analyze results
high_risk = [r for r in results if r['rule_output']['overall_risk'] in ['HIGH', 'CRITICAL']]
print(f"High-risk cases: {len(high_risk)}/{len(patients)}")
```

### Use Case 3: Care-Level Specific
```python
import requests

def get_recommendations(query, care_level):
    response = requests.post(
        "http://localhost:8000/query",
        json={
            "query": query,
            "care_level": care_level
        }
    )
    return response.json()

# ASHA worker level
asha_result = get_recommendations(
    "38-year-old with high BP",
    care_level="ASHA"
)

# PHC level
phc_result = get_recommendations(
    "38-year-old with high BP",
    care_level="PHC"
)

# District hospital level
district_result = get_recommendations(
    "38-year-old with high BP",
    care_level="DISTRICT"
)
```

---

## 📊 Understanding the Response

### Key Fields

**Risk Assessment:**
```python
data['rule_output']['overall_risk']  # LOW, MODERATE, HIGH, CRITICAL
data['rule_output']['total_score']   # Numeric score
data['rule_output']['risk_flags']    # Detailed risk factors
```

**Confidence:**
```python
data['confidence']['score']  # 0-1
data['confidence']['level']  # HIGH, MEDIUM, LOW
```

**Clinical Features:**
```python
data['features']['age']
data['features']['systolic_bp']
data['features']['hemoglobin']
data['features']['twin_pregnancy']
```

**Answer:**
```python
data['answer']  # Full clinical response
```

---

## 🔧 Configuration

### Change Port
```python
# In api_server.py
uvicorn.run(
    "api_server:app",
    host="0.0.0.0",
    port=8080,  # Change port
    reload=True
)
```

### Change Care Level Default
```python
# In config_production.py
DEFAULT_CARE_LEVEL = 'CHC'  # Change from PHC
```

---

## 🐛 Troubleshooting

### Problem: Server won't start
**Check:**
1. Is Ollama running? `ollama serve`
2. Is FAISS index built? `python main.py --ingest`
3. Are dependencies installed? `pip install -r requirements_api.txt`

### Problem: Slow responses
**Solutions:**
1. Use GPU for embeddings
2. Reduce `FAISS_TOP_K` in config
3. Use faster LLM model

### Problem: Connection refused
**Check:**
1. Server is running: `curl http://localhost:8000/health`
2. Port is not blocked by firewall
3. Correct URL in client code

---

## 📚 Next Steps

1. **Explore API Docs:** Visit `http://localhost:8000/docs`
2. **Read Full Documentation:** See `API_DOCUMENTATION.md`
3. **Run Tests:** `python test_api.py`
4. **Customize:** Modify `api_server.py` for your needs

---

## 🎉 You're Ready!

Your Medical RAG API is now running and ready to process clinical queries!

**API Endpoints:**
- Health: `http://localhost:8000/health`
- Query: `http://localhost:8000/query`
- Docs: `http://localhost:8000/docs`

**Test it:**
```bash
python test_api.py
```

---

**Happy Coding!** 🚀
