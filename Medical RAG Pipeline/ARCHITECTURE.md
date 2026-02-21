# Enhanced RAG Pipeline Architecture

## Overview
This is a production-ready, clinically-aware RAG system for High-Risk Pregnancy (HRP) detection from medical documents. The system addresses common RAG failures in medical domains through structured feature extraction, evidence-based risk scoring, and controlled generation.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                               │
│              "38-year-old with BP 150/95, Hb 10.5"              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: QUERY PREPROCESSING (clinical_preprocessor.py)        │
│  ─────────────────────────────────────────────────────────────  │
│  • Extract structured features: age, BP, Hb, glucose, etc.      │
│  • Normalize clinical concepts (age ≥35 → advanced maternal age)│
│  • Rewrite query for semantic search                            │
│  Output: ClinicalFeatures + rewritten_query                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: CLINICAL RISK SCORING (clinical_risk_scorer.py)       │
│  ─────────────────────────────────────────────────────────────  │
│  • Apply evidence-based risk rules                              │
│  • Score: Advanced age +3, Hypertension +3, Anemia +2, etc.     │
│  • Classify: Low / Moderate / High / Critical                   │
│  Output: RiskAssessment with score, factors, recommendations    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: ENHANCED RETRIEVAL (enhanced_retriever.py)            │
│  ─────────────────────────────────────────────────────────────  │
│  Stage 1: FAISS vector search (top_k=30, with MMR)              │
│  Stage 2: Hybrid keyword fallback (feature-aware)               │
│  Stage 3: Deduplication (remove near-duplicates)                │
│  Stage 4: Cross-encoder reranking                               │
│  Stage 5: Clinical rule-based boosting                          │
│           - Boost age chunks ONLY if age ≥35                    │
│           - Boost anemia chunks ONLY if Hb <11                  │
│           - Boost hypertension chunks ONLY if BP high           │
│  Output: Top-k chunks with confidence (high/medium/low)         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: CONTROLLED GENERATION (controlled_generator.py)       │
│  ─────────────────────────────────────────────────────────────  │
│  • Select system prompt based on confidence                     │
│  • Inject risk assessment into prompt                           │
│  • Call LLM with temperature=0.0 (deterministic)                │
│  • Post-process: Add confidence badges, clinical warnings       │
│  Output: Grounded answer with citations                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL RESULT                                  │
│  • Answer with confidence badge                                 │
│  • Risk assessment summary                                      │
│  • Retrieved chunks metadata                                    │
│  • Debug info (optional)                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### 1. clinical_preprocessor.py
**Purpose:** Extract structured clinical data from free text queries

**Key Features:**
- Regex-based extraction of vitals (age, BP, Hb, glucose)
- Boolean flags for conditions (twins, previous C-section, etc.)
- Risk categorization (age → advanced_maternal_age, Hb → anemia_risk)
- Query rewriting for better semantic search

**Design Decision:** 
We extract features BEFORE retrieval to enable feature-aware search and prevent retrieval bias. For example, if age=38, we add "advanced maternal age" to the query, ensuring age-risk documents are retrieved.

### 2. clinical_risk_scorer.py
**Purpose:** Evidence-based risk scoring independent of retrieval

**Key Features:**
- Rule-based scoring: Advanced age +3, Hypertension +3, Severe anemia +3
- Risk level classification: Low (0-1), Moderate (2-4), High (5-7), Critical (8+)
- Clinical recommendations based on risk factors
- Transparent rationale for each risk factor

**Design Decision:**
Risk scoring happens BEFORE generation to guide the LLM. This prevents the LLM from missing obvious risks due to poor retrieval. For example, if age=38 and BP=150/95, the system scores this as HIGH RISK even if retrieval is weak.

### 3. enhanced_retriever.py
**Purpose:** High-recall, low-bias retrieval with clinical awareness

**Key Features:**
- Increased fetch_k (30) for better recall
- Max Marginal Relevance (MMR) for diversity
- Hybrid keyword search (feature-aware)
- Deduplication to remove redundant chunks
- Cross-encoder reranking
- **Clinical rule-based boosting** (prevents lab value bias)

**Design Decision - Clinical Boosting:**
This is the KEY innovation that solves the "anemia false positive" problem:
- Boost anemia chunks ONLY if Hb < 11 (not for normal Hb)
- Boost age-risk chunks ONLY if age ≥ 35
- Boost hypertension chunks ONLY if BP ≥ 140/90

This prevents FAISS from retrieving anemia documents just because "Hb" appears in the query, even when Hb is normal.

### 4. controlled_generator.py
**Purpose:** Safe, grounded LLM generation with confidence adaptation

**Key Features:**
- Three system prompts (high/medium/low confidence)
- Risk assessment injection into prompt
- Temperature=0.0 for deterministic output
- Confidence badges and clinical warnings
- Smart fallback for no-context scenarios

**Design Decision:**
We adapt the system prompt based on retrieval confidence. High confidence → strict grounding. Low confidence → acknowledge limitations and suggest alternatives. This prevents hallucinations when retrieval is weak.

### 5. enhanced_rag_pipeline.py
**Purpose:** Orchestrate all components into a cohesive pipeline

**Key Features:**
- Sequential execution of all layers
- Debug mode for full transparency
- Logging for production monitoring
- Backward-compatible API

## Key Design Decisions

### 1. Why Extract Features Before Retrieval?
**Problem:** FAISS retrieves based on semantic similarity, but medical risk depends on specific thresholds (age ≥35, Hb <11, BP ≥140/90).

**Solution:** Extract features first, then use them to:
- Rewrite the query with clinical terminology
- Boost relevant chunks during reranking
- Score risk independently of retrieval quality

### 2. Why Rule-Based Risk Scoring?
**Problem:** LLMs can miss obvious risks if retrieval is poor.

**Solution:** Apply evidence-based rules BEFORE generation. This ensures that a 38-year-old with BP 150/95 is always flagged as high-risk, regardless of what FAISS retrieves.

### 3. Why Clinical Reranking Boost?
**Problem:** FAISS has numeric bias - it retrieves anemia documents whenever "Hb" appears, even if Hb is normal (e.g., Hb 12.5).

**Solution:** Apply conditional boosting:
```python
if features.anemia_risk and "anemia" in features.anemia_risk:
    if "anemia" in chunk_content:
        boost += 0.12  # Only boost if Hb is actually low
```

### 4. Why Confidence-Based Prompts?
**Problem:** LLMs hallucinate when forced to answer with weak context.

**Solution:** Adapt the system prompt:
- High confidence → "Answer strictly from context"
- Medium confidence → "Answer with caution, note gaps"
- Low confidence → "Acknowledge limitations, suggest alternatives"

### 5. Why Temperature=0.0?
**Problem:** Medical answers must be deterministic and reproducible.

**Solution:** Set temperature=0.0 for all LLM calls. Same query → same answer.

## Performance Characteristics

### Recall (Catching All Risks)
- ✅ High: Feature extraction + increased fetch_k + hybrid search
- ✅ Age-based risks: Always detected via feature extraction
- ✅ Vital-based risks: Extracted and scored before retrieval

### Precision (No False Positives)
- ✅ High: Clinical boosting prevents lab value bias
- ✅ Anemia: Only flagged if Hb < 11 (not for normal Hb)
- ✅ Hypertension: Only flagged if BP ≥ 140/90

### Hallucination Prevention
- ✅ Confidence-based prompts
- ✅ Temperature=0.0
- ✅ Risk scoring independent of LLM
- ✅ Explicit fallback for no-context scenarios

### Transparency
- ✅ Debug mode shows all intermediate steps
- ✅ Risk factors with rationale
- ✅ Retrieved chunks with scores
- ✅ Confidence badges on answers

## Usage Examples

### Basic Usage
```python
from enhanced_rag_pipeline import EnhancedRAGPipeline

pipeline = EnhancedRAGPipeline()
result = pipeline.run("38-year-old with BP 150/95 and Hb 10.5")
print(result['answer'])
```

### Debug Mode
```python
result = pipeline.run(query, debug=True)
print(result['debug']['extracted_features'])
print(result['debug']['risk_factors_detail'])
print(result['debug']['retrieved_chunks'])
```

### CLI Usage
```bash
# Single query
python main.py --query "Twin pregnancy with previous cesarean"

# Interactive mode
python main.py --interactive

# Evaluation mode
python main.py --evaluate
```

## Testing Strategy

### Unit Tests (Recommended)
- Test feature extraction with edge cases
- Test risk scoring with known scenarios
- Test clinical boosting logic
- Test confidence determination

### Integration Tests
- Test full pipeline with sample queries
- Verify risk detection for known high-risk cases
- Verify no false positives for normal cases

### Evaluation Queries
```python
test_cases = [
    # Should detect high-risk
    ("38-year-old with BP 150/95", "high"),
    ("Twin pregnancy with previous cesarean", "high"),
    ("Hb 6.5 g/dL in pregnancy", "high"),
    
    # Should NOT detect high-risk
    ("25-year-old with normal vitals", "low"),
    ("Hb 12.5 g/dL, BP 120/80", "low"),
]
```

## Maintenance Guidelines

### Adding New Risk Factors
1. Update `ClinicalPreprocessor` to extract the feature
2. Add scoring rule to `ClinicalRiskScorer.RISK_SCORES`
3. Add boosting logic to `EnhancedRetriever._apply_clinical_reranking`
4. Update documentation

### Tuning Retrieval
- Adjust `fetch_k` in `enhanced_retriever.py` (higher = more recall)
- Adjust MMR `lambda_mult` (0.7 = balanced, 1.0 = pure relevance)
- Adjust boost values in clinical reranking (0.10-0.15 typical)

### Tuning Confidence Thresholds
- Adjust in `EnhancedRetriever._determine_confidence`
- High: top_score ≥ 0.3, num_chunks ≥ 3
- Medium: top_score ≥ 0.1, num_chunks ≥ 2

## Future Enhancements

1. **External Reranker:** Replace cross-encoder with medical-specific reranker
2. **BM25 Integration:** Add proper BM25 for keyword search (currently simple matching)
3. **Multi-Document Support:** Extend to multiple clinical guidelines
4. **Temporal Reasoning:** Handle gestational age-dependent risks
5. **Structured Output:** Return JSON schema for downstream systems
6. **Active Learning:** Log low-confidence queries for human review

## Dependencies

- `langchain` - Vector store and embeddings
- `faiss-cpu` - Vector similarity search
- `sentence-transformers` - Cross-encoder reranking
- `requests` - Ollama API calls
- `PyMuPDF` - PDF parsing (for ingestion)

## License & Disclaimer

This is a research/educational system. NOT for clinical use without validation.
All clinical decisions must be verified by qualified healthcare professionals.
