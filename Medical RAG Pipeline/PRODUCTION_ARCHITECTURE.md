# Production-Grade Medical RAG Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY (Free Text)                        │
│   "38-year-old with BP 150/95, Hb 10.5, twin pregnancy"        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: CLINICAL FEATURE EXTRACTION (Deterministic)            │
│  ─────────────────────────────────────────────────────────────  │
│  • Regex + LLM hybrid extraction                                 │
│  • Unit normalization (mmHg, g/dL, mg/dL)                       │
│  • Missing field handling                                        │
│  • Structured output: {age, BP, Hb, FBS, comorbidities, ...}   │
│  Output: ClinicalFeatures + extractor_confidence                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: HYBRID RETRIEVAL (FAISS + BM25 + Reranking)          │
│  ─────────────────────────────────────────────────────────────  │
│  Stage 1: Query Rewriting                                        │
│    "Advanced maternal age pregnancy risk classification         │
│     India guidelines Hb 10.5 anemia threshold pregnancy"        │
│                                                                  │
│  Stage 2: Dual Retrieval                                         │
│    • Dense: FAISS (L2-normalized, cosine similarity)            │
│    • Sparse: BM25 keyword search                                │
│                                                                  │
│  Stage 3: Reciprocal Rank Fusion                                │
│    Merge FAISS + BM25 results                                   │
│                                                                  │
│  Stage 4: Cross-Encoder Reranking                               │
│    bge-reranker or MiniLM cross-encoder                         │
│                                                                  │
│  Stage 5: Score Normalization                                   │
│    Convert distances → similarities [0, 1]                      │
│                                                                  │
│  Output: Top-k chunks + retrieval_quality score                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: CLINICAL RULE ENGINE (Authoritative)                  │
│  ─────────────────────────────────────────────────────────────  │
│  Hard Rules (Override LLM):                                      │
│    • Age ≥35 → Advanced maternal age → HIGH RISK                │
│    • Hb <11 → Anaemia                                           │
│    • BP ≥140/90 → Hypertension → HIGH RISK                      │
│    • Twin pregnancy → HIGH RISK                                 │
│                                                                  │
│  Output: Structured risk flags + rule_coverage score            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: EVIDENCE-GROUNDED REASONING                           │
│  ─────────────────────────────────────────────────────────────  │
│  LLM Reasoning ONLY from:                                        │
│    • Retrieved chunks (with page citations)                     │
│    • Rule engine output                                         │
│                                                                  │
│  Hallucination Guards:                                           │
│    IF retrieval_quality < 0.35 OR chunks irrelevant             │
│    THEN: "LOW CONFIDENCE — INSUFFICIENT DOCUMENT EVIDENCE"      │
│                                                                  │
│  Output: Evidence-grounded answer + confidence breakdown        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL OUTPUT                                  │
│  [CLINICAL DECISION SUPPORT — NOT A DIAGNOSIS]                  │
│                                                                  │
│  Risk Classification:                                            │
│    - Advanced maternal age: Present                             │
│    - Anaemia: Present (Hb 10.5 < 11)                           │
│    - Hypertension: Present (BP 150/95 ≥ 140/90)                │
│                                                                  │
│  Overall Risk: HIGH RISK (rule-based)                           │
│                                                                  │
│  Evidence:                                                       │
│    - Page 5: "Advanced maternal age (≥35) increases risk..."   │
│    - Page 14: "Anaemia defined as Hb <11 g/dL"                 │
│                                                                  │
│  Confidence: 0.82 (High)                                        │
│    - Retrieval quality: 0.85                                    │
│    - Rule coverage: 1.00                                        │
│    - Chunk agreement: 0.70                                      │
│    - Extractor confidence: 0.95                                 │
│                                                                  │
│  [Consult qualified physician for clinical decisions]           │
└─────────────────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

### 1. Deterministic Feature Extraction
- Regex patterns for structured data (age, BP, Hb)
- LLM fallback for complex cases
- Unit normalization (automatic conversion)
- Confidence scoring per field

### 2. Hybrid Retrieval
- FAISS for semantic similarity
- BM25 for exact keyword matching
- RRF for optimal fusion
- Cross-encoder for final reranking

### 3. Rule Engine as Authority
- Runs BEFORE LLM reasoning
- Hard-coded medical thresholds
- Cannot be overridden by LLM
- Provides ground truth

### 4. Hallucination Prevention
- Strict confidence thresholds
- Evidence requirement
- "Not found" fallback
- No speculative reasoning

## Confidence Formula

```python
confidence = (
    0.4 * retrieval_quality +      # Avg top-3 similarity
    0.3 * rule_coverage +           # % features with rules
    0.2 * chunk_agreement +         # Multi-chunk support
    0.1 * extractor_confidence      # Feature extraction quality
)
```

## Safety Layers

1. **Medical Disclaimer** - Always prepended
2. **Confidence Threshold** - Block low-confidence outputs
3. **Evidence Requirement** - Must cite sources
4. **Rule Override** - Rules trump LLM
5. **Debug Telemetry** - Full transparency

## File Structure

```
production_rag/
├── layer1_extractor.py          # Clinical feature extraction
├── layer2_retrieval.py          # Hybrid retrieval system
├── layer3_rules.py              # Clinical rule engine
├── layer4_reasoning.py          # Evidence-grounded LLM
├── production_pipeline.py       # Integrated pipeline
├── confidence_scorer.py         # Weighted confidence calculation
├── hallucination_guard.py       # Safety checks
└── config_production.py         # Production configuration
```
