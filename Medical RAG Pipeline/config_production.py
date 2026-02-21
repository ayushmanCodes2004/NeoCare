# ============================================================
# config_production.py — Production configuration
# ============================================================

import os

# ============================================================
# PATHS
# ============================================================
PDF_PATH = "jogh-13-04116_merged.pdf"
FAISS_INDEX_DIR = "./faiss_medical_index"
LOG_FILE = "medical_rag.log"

# ============================================================
# CHUNKING PARAMETERS (Optimized for medical documents)
# ============================================================
CHUNK_SIZE = 400  # 300-500 tokens as specified
CHUNK_OVERLAP = 80  # 20% overlap
MIN_CHUNK_LENGTH = 100

# ============================================================
# RETRIEVAL PARAMETERS
# ============================================================
# FAISS
FAISS_TOP_K = 30  # Initial fetch
FAISS_FINAL_K = 8  # Final chunks after reranking

# BM25
BM25_TOP_K = 10

# Reranking
RERANK_TOP_K = 8
# Using medical-optimized reranker (better than ms-marco for medical domain)
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-12-v2"  # Larger, more accurate
# Alternative: "BAAI/bge-reranker-base" or "BAAI/bge-reranker-large" for best results

# Score normalization
MIN_SIMILARITY_THRESHOLD = 0.35  # Below this = low confidence

# ============================================================
# CONFIDENCE SCORING WEIGHTS
# ============================================================
CONFIDENCE_WEIGHTS = {
    'retrieval_quality': 0.4,
    'rule_coverage': 0.3,
    'chunk_agreement': 0.2,
    'extractor_confidence': 0.1,
}

# Confidence thresholds (STRICT MAPPING - never override)
CONFIDENCE_THRESHOLDS = {
    'high': 0.85,      # >= 0.85 → HIGH
    'medium': 0.60,    # 0.60-0.85 → MEDIUM  
    'low': 0.35,       # < 0.60 → LOW
}

# ============================================================
# CLINICAL RULE THRESHOLDS
# ============================================================
CLINICAL_THRESHOLDS = {
    # Age
    'advanced_maternal_age': 35,
    'teenage_pregnancy_max': 18,
    
    # Hemoglobin (g/dL)
    'severe_anemia': 7.0,
    'moderate_anemia': 10.0,
    'mild_anemia': 11.0,
    
    # Blood Pressure (mmHg)
    'severe_hypertension_systolic': 160,
    'severe_hypertension_diastolic': 110,
    'hypertension_systolic': 140,
    'hypertension_diastolic': 90,
    
    # Glucose (mg/dL)
    'diabetes_fbs': 126,
    'gdm_fbs': 92,
    'diabetes_ogtt': 200,
    'gdm_ogtt': 140,
}

# ============================================================
# LLM PARAMETERS
# ============================================================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:7b-instruct"
EMBEDDING_MODEL = "nomic-embed-text"

TEMPERATURE = 0.0  # Deterministic for medical
MAX_TOKENS = 1024
TOP_P = 1.0
REPEAT_PENALTY = 1.1

# ============================================================
# MEDICAL SAFETY
# ============================================================
MEDICAL_DISCLAIMER = """[CLINICAL DECISION SUPPORT — NOT A DIAGNOSIS]
This is an AI-powered clinical decision support tool for frontline health workers.
All recommendations must be verified by a qualified healthcare professional before any clinical action is taken.
This system provides guidance, not authority. Final management decisions should be made by a qualified doctor."""

HALLUCINATION_GUARD_THRESHOLD = 0.0  # Disabled for testing - allows all outputs

# ============================================================
# CARE LEVEL AWARENESS (Rural India Context)
# ============================================================
CARE_LEVELS = {
    'ASHA': {
        'name': 'ASHA Worker / Community Level',
        'allowed_actions': ['recognize', 'refer', 'educate', 'follow_up'],
        'forbidden_treatments': [
            'prescribe medication',
            'administer drugs',
            'perform procedures',
            'diagnostic tests',
        ],
    },
    'PHC': {
        'name': 'Primary Health Center',
        'allowed_actions': ['stabilize', 'refer', 'basic_treatment', 'monitoring'],
        'forbidden_treatments': [
            'specialist procedures',
            'advanced imaging',
            'intensive care',
            'surgical intervention',
        ],
    },
    'CHC': {
        'name': 'Community Health Center',
        'allowed_actions': ['treat', 'stabilize', 'refer_if_needed', 'specialist_consult'],
        'forbidden_treatments': [
            'tertiary procedures',
            'nicu',
            'advanced surgery',
        ],
    },
    'DISTRICT': {
        'name': 'District Hospital / Tertiary Center',
        'allowed_actions': ['full_treatment', 'specialist_care', 'procedures', 'icu'],
        'forbidden_treatments': [],
    },
}

# Default care level for rural deployment
DEFAULT_CARE_LEVEL = 'PHC'

# Specialist treatments that need care-level filtering
SPECIALIST_TREATMENTS = [
    'blood transfusion',
    'intensive care',
    'ventilator',
    'dialysis',
    'surgery',
    'cesarean section',
    'nicu admission',
    'specialist consultation',
    'advanced imaging',
    'mri',
    'ct scan',
]

# ============================================================
# DEBUG SETTINGS
# ============================================================
DEBUG_MODE = True  # Always show telemetry
VERBOSE_LOGGING = True

# ============================================================
# CLINICAL TAGS (for metadata)
# ============================================================
CLINICAL_TAGS = {
    'anaemia': ['anaemia', 'anemia', 'hemoglobin', 'haemoglobin', 'hb', 'iron', 'ifa'],
    'hypertension': ['hypertension', 'blood pressure', 'bp', 'pre-eclampsia', 'preeclampsia', 'pih', 'eclampsia'],
    'diabetes': ['diabetes', 'gdm', 'glucose', 'fbs', 'rbs', 'ogtt', 'insulin'],
    'age_risk': ['age', 'maternal age', 'elderly', 'teenage', 'adolescent'],
    'twins': ['twin', 'multiple pregnancy', 'multiple gestation'],
    'cesarean': ['cesarean', 'caesarean', 'lscs', 'c-section'],
    'placenta': ['placenta previa', 'placenta praevia', 'aph'],
    'iugr': ['iugr', 'growth restriction', 'sga'],
    'hypothyroid': ['hypothyroid', 'tsh', 'thyroid'],
}
