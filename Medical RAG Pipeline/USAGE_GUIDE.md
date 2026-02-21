# Enhanced RAG System - Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Command-Line Interface](#command-line-interface)
4. [Python API](#python-api)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.8+
- Ollama installed and running
- 8GB+ RAM recommended

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install and Start Ollama
```bash
# Install Ollama (see https://ollama.ai)
# On macOS/Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve
```

### Step 3: Pull Required Models
```bash
# LLM model for generation
ollama pull mistral:7b-instruct

# Embedding model for retrieval
ollama pull nomic-embed-text
```

### Step 4: Ingest Documents
```bash
python main.py --ingest
```

This will:
- Parse the PDF document
- Chunk it intelligently
- Generate embeddings
- Store in FAISS index

## Quick Start

### Single Query
```bash
python main.py --query "38-year-old pregnant woman with BP 150/95"
```

### Interactive Mode
```bash
python main.py --interactive
```

Then type queries interactively:
```
Query> 38-year-old with high blood pressure
Query> Twin pregnancy with previous cesarean
Query> What is the prevalence of HRP in India?
Query> exit
```

## Command-Line Interface

### Available Commands

#### 1. Ingest Documents
```bash
python main.py --ingest
```
Parses PDF and creates FAISS index. Run this once before querying.

#### 2. Single Query
```bash
python main.py --query "YOUR QUESTION HERE"
```
Runs a single query and displays results with full debug information.

#### 3. Interactive Mode
```bash
python main.py --interactive
```
Starts an interactive REPL for multiple queries.

#### 4. Evaluation Mode
```bash
python main.py --evaluate
```
Runs evaluation test suite (if evaluate.py is configured).

## Python API

### Basic Usage

```python
from enhanced_rag_pipeline import EnhancedRAGPipeline

# Initialize pipeline
pipeline = EnhancedRAGPipeline()

# Run query
result = pipeline.run("38-year-old with BP 150/95")

# Print answer
print(result['answer'])
```

### With Debug Information

```python
# Run with debug mode
result = pipeline.run(
    query="Twin pregnancy with previous cesarean",
    debug=True,
    verbose=True
)

# Access debug information
print("Extracted Features:", result['debug']['extracted_features'])
print("Risk Factors:", result['debug']['risk_factors_detail'])
print("Retrieved Chunks:", result['debug']['retrieved_chunks'])
```

### Format and Display Results

```python
# Format result as human-readable text
formatted = pipeline.format_result(result, include_debug=True)
print(formatted)
```

### Access Individual Components

```python
from clinical_preprocessor import ClinicalPreprocessor
from clinical_risk_scorer import ClinicalRiskScorer

# Feature extraction only
preprocessor = ClinicalPreprocessor()
result = preprocessor.process_query("38-year-old with BP 150/95")
features = result['extracted_features']
print(f"Age: {features.age}")
print(f"BP: {features.systolic_bp}/{features.diastolic_bp}")

# Risk scoring only
scorer = ClinicalRiskScorer()
assessment = scorer.score_risk(features)
print(f"Risk Level: {assessment.risk_level}")
print(f"Risk Score: {assessment.total_score}")
```

## Configuration

### Retrieval Parameters (config.py)

```python
# Number of chunks to retrieve
TOP_K_RETRIEVAL = 10  # Increase for more context

# Initial fetch size (before filtering)
FAISS_FETCH_K = 30  # Increase for better recall

# Similarity threshold (L2 distance)
SIMILARITY_THRESHOLD = 1.3  # Lower = stricter

# Reranker threshold
RERANK_SCORE_THRESHOLD = 0.05  # Lower = stricter
```

### LLM Parameters (config.py)

```python
# Model selection
OLLAMA_MODEL = "mistral:7b-instruct"  # Or "llama2:13b", etc.

# Temperature (MUST be 0.0 for medical)
TEMPERATURE = 0.0  # Deterministic output

# Max tokens
MAX_TOKENS = 1024  # Increase for longer answers
```

### Risk Scoring (clinical_risk_scorer.py)

```python
RISK_SCORES = {
    'advanced_maternal_age': 3,  # Adjust weights
    'hypertensive': 3,
    'severe_anemia': 3,
    'gestational_diabetes': 3,
    # Add more conditions as needed
}

RISK_THRESHOLDS = {
    'low': (0, 1),
    'moderate': (2, 4),
    'high': (5, 7),
    'critical': (8, 100),
}
```

### Clinical Boosting (enhanced_retriever.py)

```python
# Adjust boost values in _apply_clinical_reranking method
if features.age_risk_category == "advanced_maternal_age":
    boost += 0.15  # Increase to prioritize age-risk chunks

if features.anemia_risk and "anemia" in features.anemia_risk:
    boost += 0.12  # Increase to prioritize anemia chunks
```

## Testing

### Run Test Suite
```bash
python test_enhanced_rag.py
```

This tests:
1. Feature extraction
2. Risk scoring
3. Query rewriting
4. End-to-end pipeline (if FAISS index available)

### Manual Testing

```python
from enhanced_rag_pipeline import EnhancedRAGPipeline

pipeline = EnhancedRAGPipeline()

# Test high-risk case
result = pipeline.run("38-year-old with BP 150/95 and Hb 6.5")
assert result['risk_assessment']['risk_level'] in ['high', 'critical']

# Test normal case
result = pipeline.run("25-year-old with normal vitals")
assert result['risk_assessment']['risk_level'] == 'low'
```

## Example Queries

### High-Risk Pregnancy Detection

```python
queries = [
    # Age-based risk
    "38-year-old pregnant woman",
    "42-year-old primigravida",
    "17-year-old adolescent pregnancy",
    
    # Vital-based risk
    "BP 160/110 in pregnancy",
    "Hemoglobin 6.5 g/dL",
    "Fasting blood sugar 140 mg/dL",
    
    # Obstetric history
    "Twin pregnancy",
    "Previous cesarean section",
    "Placenta previa",
    
    # Combined risks
    "38-year-old with BP 150/95 and Hb 10.5",
    "Twin pregnancy with previous cesarean and diabetes",
    
    # Normal cases
    "25-year-old with normal vitals",
    "Hb 12.5, BP 120/80, age 28",
]

for query in queries:
    result = pipeline.run(query, verbose=False)
    print(f"Query: {query}")
    print(f"Risk: {result['risk_assessment']['risk_level'].upper()}")
    print()
```

### Document Questions

```python
queries = [
    "What is the prevalence of high-risk pregnancy in India?",
    "How to manage hypertension in pregnancy?",
    "What are the drug dosages for eclampsia management?",
    "What government schemes support pregnant women?",
]

for query in queries:
    result = pipeline.run(query, verbose=False)
    print(f"Q: {query}")
    print(f"A: {result['answer'][:200]}...")
    print()
```

## Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# In another terminal, verify models are pulled
ollama list
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull required models
ollama pull mistral:7b-instruct
ollama pull nomic-embed-text
```

### Issue: "FAISS index not found"

**Solution:**
```bash
# Run ingestion first
python main.py --ingest
```

### Issue: Low retrieval quality

**Solutions:**
1. Increase `FAISS_FETCH_K` in config.py (e.g., 50)
2. Lower `SIMILARITY_THRESHOLD` (e.g., 1.5)
3. Adjust clinical boosting values in enhanced_retriever.py

### Issue: Hallucinations in answers

**Solutions:**
1. Verify `TEMPERATURE = 0.0` in config.py
2. Check confidence level - low confidence may indicate weak retrieval
3. Review system prompts in controlled_generator.py

### Issue: Missing risk factors

**Solutions:**
1. Check feature extraction: `preprocessor.process_query(query)`
2. Verify risk scoring rules in clinical_risk_scorer.py
3. Add new patterns to clinical_preprocessor.py if needed

## Advanced Usage

### Custom Feature Extraction

```python
from clinical_preprocessor import ClinicalPreprocessor

class CustomPreprocessor(ClinicalPreprocessor):
    def extract_features(self, query):
        features = super().extract_features(query)
        
        # Add custom feature extraction
        if 'obesity' in query.lower():
            features.bmi_risk = 'obese'
        
        return features
```

### Custom Risk Scoring

```python
from clinical_risk_scorer import ClinicalRiskScorer

class CustomScorer(ClinicalRiskScorer):
    RISK_SCORES = {
        **ClinicalRiskScorer.RISK_SCORES,
        'obesity': 2,  # Add new risk factor
    }
```

### Batch Processing

```python
from enhanced_rag_pipeline import EnhancedRAGPipeline
import json

pipeline = EnhancedRAGPipeline()

# Load queries from file
with open('queries.txt', 'r') as f:
    queries = f.readlines()

# Process batch
results = []
for query in queries:
    result = pipeline.run(query.strip(), verbose=False)
    results.append({
        'query': query.strip(),
        'risk_level': result['risk_assessment']['risk_level'],
        'risk_score': result['risk_assessment']['total_score'],
        'answer': result['answer'],
    })

# Save results
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Integration with Web API

```python
from flask import Flask, request, jsonify
from enhanced_rag_pipeline import EnhancedRAGPipeline

app = Flask(__name__)
pipeline = EnhancedRAGPipeline()

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query')
    
    result = pipeline.run(query_text, debug=False, verbose=False)
    
    return jsonify({
        'answer': result['answer'],
        'risk_assessment': result['risk_assessment'],
        'confidence': result['confidence'],
    })

if __name__ == '__main__':
    app.run(port=5000)
```

## Performance Tips

1. **First Query is Slow:** Model loading takes time. Subsequent queries are faster.

2. **Memory Usage:** FAISS index and models require ~4-6GB RAM. Close other applications if needed.

3. **Retrieval Speed:** Reduce `FAISS_FETCH_K` for faster retrieval (trade-off with recall).

4. **Generation Speed:** Use smaller models (e.g., `mistral:7b` instead of `llama2:13b`) for faster generation.

5. **Batch Processing:** Reuse the same pipeline instance to avoid reloading models.

## Best Practices

1. **Always use debug mode during development** to understand system behavior
2. **Test with known high-risk and normal cases** to validate risk detection
3. **Review confidence levels** - low confidence may indicate need for better retrieval tuning
4. **Log all queries and results** for continuous improvement
5. **Validate clinical claims** against source documents before deployment

## Support

For issues, questions, or contributions:
- See ARCHITECTURE.md for design details
- See README_ENHANCED.md for system overview
- Run test_enhanced_rag.py to validate installation
