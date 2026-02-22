# ============================================================
# config.py — All configuration constants for Medical RAG
# ============================================================

import os

PDF_PATH = "jogh-13-04116_merged.pdf"
FAISS_INDEX_DIR = "./faiss_medical_index"

# ----------------------------
# CHUNKING PARAMETERS
# ----------------------------
CHUNK_SIZE = 600           # tokens approx — smaller for clinical guidelines
CHUNK_OVERLAP = 100        # preserve sentence context across chunk boundaries
MIN_CHUNK_LENGTH = 80      # discard boilerplate/noise chunks below this char count
PROCEDURE_CHUNK_SIZE = 400 # smaller chunks for dense procedure chart pages (pages 26-35)

# ----------------------------
# RETRIEVAL THRESHOLDS (DETERMINISTIC GATES)
# ----------------------------
TOP_K_RETRIEVAL = 10             # final pool size after metadata filtering (higher for medical recall)
TOP_K_RERANK = 5                 # after reranking, top results sent to LLM
FAISS_FETCH_K = 30               # initial broad fetch from FAISS (before metadata filtering)
SIMILARITY_THRESHOLD = 1.3       # FAISS L2 distance threshold (lower=more similar)
                                  # L2 > 1.3 ≈ cosine similarity < 0.25 → discard
RERANK_SCORE_THRESHOLD = 0.05    # cross-encoder minimum score (lower = more permissive for medical recall)
KEYWORD_MATCH_BOOST = 3          # number of keyword-matched chunks to inject into retrieval pool

# ----------------------------
# CONFIDENCE TIER THRESHOLDS
# ----------------------------
CONFIDENCE_HIGH_MIN_CHUNKS = 3       # need at least 3 reranked chunks for high confidence
CONFIDENCE_HIGH_MIN_SCORE = 0.3      # top rerank score must be >= 0.3 for high confidence
CONFIDENCE_MEDIUM_MIN_CHUNKS = 1     # at least 1 reranked chunk for medium confidence
CONFIDENCE_MEDIUM_MIN_SCORE = 0.05   # top rerank score must be >= 0.05 for medium confidence
CONFIDENCE_LOW_FALLBACK_K = 3        # even at low confidence, try to return top 3 loosest chunks

# ----------------------------
# LLM PARAMETERS (OpenAI)
# ----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")  # Set via environment variable
OPENAI_MODEL = "gpt-4o-mini"  # or "gpt-4o" for better quality
TEMPERATURE = 0.0          # MUST be 0.0 for medical RAG — deterministic output
MAX_TOKENS = 1024
TOP_P = 1.0

# ----------------------------
# EMBEDDING (OpenAI)
# ----------------------------
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI embedding model

# ----------------------------
# LOGGING
# ----------------------------
LOG_FILE = "medical_rag.log"

# ----------------------------
# PAGE TYPE MAP (exact page ranges from this PDF)
# ----------------------------
PAGE_TYPE_RANGES = {
    "research_paper": list(range(1, 11)),          # pages 1-10
    "clinical_guideline": list(range(11, 23)),     # pages 11-22
    "government_policy": list(range(23, 26)),      # pages 23-25
    "procedure_chart": list(range(26, 36)),        # pages 26-35
    "monitoring_checklist": list(range(36, 60)),   # pages 36-49+
}

# ----------------------------
# CONDITION KEYWORD MAP
# ----------------------------
CONDITION_KEYWORDS = {
    "anaemia": ["haemoglobin", "hemoglobin", "hb", "anaemia", "anemia", "ifa",
                "iron", "folic acid", "pallor"],
    "hypertension": ["hypertension", "pih", "pre-eclampsia", "pre eclampsia",
                     "eclampsia", "bp", "blood pressure", "mgso4", "magnesium",
                     "nifedipine", "labetalol", "methyldopa", "proteinuria"],
    "GDM": ["gestational diabetes", "gdm", "ogtt", "insulin", "blood glucose",
            "plasma glucose", "pppg", "mnt", "medical nutrition"],
    "hypothyroidism": ["hypothyroidism", "tsh", "levothyroxine", "thyroid",
                       "ft4", "goiter", "iodine"],
    "syphilis": ["syphilis", "rpr", "vdrl", "penicillin", "benzathine",
                 "erythromycin", "azithromycin", "sti"],
    "IUGR": ["iugr", "intrauterine growth", "sga", "fundal height", "sfh",
             "symphysio", "small for gestational"],
    "eclampsia": ["eclampsia", "convulsion", "seizure", "magnesium sulfate",
                  "mgso4", "magsulf", "patellar jerk"],
    "PPH": ["postpartum haemorrhage", "pph", "oxytocin", "amtsl",
            "atonic", "ergometrine", "misoprostol", "carboprost", "uterine massage"],
    "placenta_previa": ["placenta previa", "placenta praevia", "aph",
                        "antepartum haemorrhage", "painless bleeding"],
    "twins": ["twins", "multiple pregnancy", "art", "assisted reproduction",
              "polyhydramnios twin", "twin to twin"],
    "previous_CS": ["caesarean", "cesarean", "lscs", "previous cs",
                    "uterine rupture", "scar tenderness"],
    "general": []  # default fallback
}

# ----------------------------
# QUESTION TYPE KEYWORDS
# ----------------------------
QUESTION_TYPE_MAP = {
    "prevalence_statistic": ["prevalence", "percentage", "how many", "proportion",
                              "rate", "odds ratio", "aor", "confidence interval",
                              "nfhs", "survey"],
    "clinical_management": ["manage", "treatment", "treat", "handle", "approach",
                             "protocol", "guideline", "care"],
    "drug_dosage": ["dose", "dosage", "mg", "units", "how much", "drug",
                    "medication", "administer", "inject", "tablet", "injection"],
    "policy_scheme": ["scheme", "yojana", "abhiyan", "government", "asha",
                      "incentive", "benefit", "fund", "pmsma", "jsy", "jssk"],
    "risk_factor": ["risk factor", "causes", "associated", "contribute",
                    "predictor", "determinant"],
    "diagnostic_criteria": ["diagnose", "diagnosis", "define", "criteria",
                             "threshold", "cutoff", "classified as"],
    "procedure_steps": ["steps", "how to", "procedure", "technique",
                        "perform", "conduct", "method"],
}

# ----------------------------
# QUERY NORMALIZATION MAP
# Converts colloquial/specific terms to medical terminology
# before embedding for much better FAISS retrieval
# ----------------------------
QUERY_NORMALIZATION_RULES = {
    "age_patterns": [
        {"pattern": r"\b(3[5-9]|4[0-9])[-\s]?year[-\s]?old\b", "replacement": "advanced maternal age elderly gravida"},
        {"pattern": r"\b(1[0-7]|adolescen)[-\s]?year[-\s]?old\b", "replacement": "teenage pregnancy adolescent pregnancy young maternal age"},
        {"pattern": r"\b(18|19|20)[-\s]?year[-\s]?old\b", "replacement": "young maternal age early pregnancy"},
        {"pattern": r"\belderly\s+pregnan\w*\b", "replacement": "advanced maternal age elderly gravida"},
        {"pattern": r"\bteen\w*\s+pregnan\w*\b", "replacement": "teenage pregnancy adolescent pregnancy"},
    ],
    "abbreviation_map": {
        "high bp": "hypertension pregnancy induced hypertension blood pressure",
        "low bp": "hypotension blood pressure",
        "high blood pressure": "hypertension pregnancy induced hypertension PIH",
        "sugar": "gestational diabetes mellitus GDM blood glucose",
        "diabetes": "gestational diabetes mellitus GDM OGTT blood glucose",
        "blood sugar": "gestational diabetes mellitus GDM plasma glucose",
        "c-section": "caesarean section previous caesarean LSCS",
        "c section": "caesarean section previous caesarean LSCS",
        "cesarean": "caesarean section previous caesarean LSCS",
        "iron deficiency": "anaemia haemoglobin iron folic acid IFA",
        "anemia": "anaemia haemoglobin hemoglobin Hb iron deficiency",
        "low hemoglobin": "anaemia haemoglobin severe anaemia",
        "low haemoglobin": "anaemia haemoglobin severe anaemia",
        "fits": "eclampsia convulsion seizure magnesium sulfate",
        "seizure": "eclampsia convulsion seizure magnesium sulfate",
        "convulsion": "eclampsia convulsion seizure magnesium sulfate MgSO4",
        "bleeding after delivery": "postpartum haemorrhage PPH oxytocin AMTSL",
        "heavy bleeding": "postpartum haemorrhage PPH antepartum haemorrhage APH",
        "twin": "twins multiple pregnancy",
        "thyroid": "hypothyroidism TSH levothyroxine thyroid",
        "growth retardation": "intrauterine growth retardation IUGR SGA fundal height",
        "baby not growing": "intrauterine growth retardation IUGR small for gestational age",
        "small baby": "intrauterine growth retardation IUGR SGA",
        "placenta low": "placenta previa APH antepartum haemorrhage painless bleeding",
        "std": "syphilis RPR VDRL sexually transmitted infection",
        "sti": "syphilis RPR VDRL sexually transmitted infection",
        "cash benefit": "incentive scheme yojana cash benefit amount",
        "money": "incentive scheme benefit amount cash",
        "government help": "government scheme yojana JSY JSSK PMSMA PMMMVY",
        "govt scheme": "government scheme yojana JSY JSSK PMSMA PMMMVY",
        "breastfeed": "breastfeeding initiation early breastfeeding",
        "delivery steps": "AMTSL active management third stage labour oxytocin",
        "checkup": "antenatal checkup ANC examination",
        "prenatal": "antenatal checkup ANC examination",
        "hrp": "high risk pregnancy high-risk pregnancy",
        "neonatal": "neonatal resuscitation newborn care",
        "newborn": "neonatal resuscitation newborn care",
    },
    "clinical_synonyms": {
        "pre-eclampsia": "pre eclampsia preeclampsia hypertensive disorders pregnancy PIH proteinuria",
        "preeclampsia": "pre-eclampsia pre eclampsia hypertensive disorders pregnancy PIH proteinuria",
        "HELLP": "HELLP syndrome pre-eclampsia severe hypertension",
        "PPH": "postpartum haemorrhage postpartum hemorrhage atonic uterine",
        "APH": "antepartum haemorrhage placenta previa bleeding",
        "AMTSL": "active management third stage labour oxytocin cord traction uterine massage",
        "GDM": "gestational diabetes mellitus OGTT blood glucose insulin",
        "IUGR": "intrauterine growth retardation restriction small for gestational age SGA",
        "PMSMA": "Pradhan Mantri Surakshit Matritva Abhiyan 9th day clinic",
        "JSY": "Janani Suraksha Yojana cash incentive institutional delivery",
        "JSSK": "Janani Shishu Suraksha Karyakaram free entitlements cashless",
        "PMMMVY": "Pradhan Mantri Matru Vandana Yojana cash benefit 5000",
        "NFHS": "National Family Health Survey NFHS-5 prevalence data",
    },
}

KEYWORD_SEARCH_TERMS = {
    "prevalence": ["prevalence", "49.4", "percentage", "NFHS", "high-risk"],
    "hypertension": ["hypertension", "pre-eclampsia", "eclampsia", "blood pressure", "BP",
                     "methyl dopa", "methyldopa", "nifedipine", "labetalol", "MgSO4"],
    "anaemia": ["anaemia", "anemia", "haemoglobin", "hemoglobin", "Hb", "IFA", "iron",
                "folic acid", "pallor", "blood transfusion"],
    "gdm": ["GDM", "gestational diabetes", "OGTT", "blood glucose", "plasma glucose",
            "insulin", "MNT", "140 mg"],
    "hypothyroidism": ["hypothyroidism", "TSH", "levothyroxine", "thyroid", "FT4"],
    "syphilis": ["syphilis", "RPR", "VDRL", "penicillin", "benzathine"],
    "iugr": ["IUGR", "intrauterine growth", "SGA", "fundal height", "small for gestational"],
    "pph": ["PPH", "postpartum", "haemorrhage", "hemorrhage", "oxytocin", "AMTSL",
            "atonic", "ergometrine", "misoprostol", "uterine massage"],
    "eclampsia": ["eclampsia", "convulsion", "seizure", "magnesium sulfate", "MgSO4",
                  "loading dose", "4 gm", "5 gm"],
    "caesarean": ["caesarean", "cesarean", "LSCS", "previous CS", "uterine rupture",
                  "scar tenderness"],
    "placenta": ["placenta previa", "APH", "antepartum", "painless bleeding"],
    "twins": ["twins", "multiple pregnancy", "polyhydramnios"],
    "scheme": ["PMSMA", "JSY", "JSSK", "PMMMVY", "yojana", "scheme", "incentive",
              "ASHA", "benefit", "cash", "government"],
    "procedure": ["AMTSL", "oxytocin", "cord traction", "uterine massage",
                  "breastfeeding", "resuscitation", "ANC", "antenatal"],
    "checklist": ["checklist", "equipment", "BP Apparatus", "Glucometer", "Fetoscope",
                  "monitoring", "annexure"],
}
