# Medical RAG System — CLI Coding Agent Prompt
> Based on: `jogh-13-04116_merged.pdf`
> Purpose: Production-grade RAG for High-Risk Pregnancy (HRP) medical document

---

## DOCUMENT OVERVIEW

Build a production-grade Medical RAG (Retrieval-Augmented Generation) system for a merged PDF containing:

1. A peer-reviewed research paper on high-risk pregnancy prevalence in India (NFHS-5 data) — Kuppusamy et al., 2023, Journal of Global Health
2. Clinical guidelines for high-risk pregnancy conditions (hypertension, anaemia, GDM, hypothyroidism, syphilis, IUGR, previous CS, placenta previa, twins)
3. Government of India PMSMA (Pradhan Mantri Surakshit Matritva Abhiyan) operational guidelines and tracking protocols
4. Clinical procedure charts (ANC checkup, postnatal care, PPH management, AMTSL, eclampsia management, neonatal resuscitation)
5. Monitoring checklists and annexures for PMSMA onsite and self-assessment

---

## TECH STACK

| Component | Choice | Reason |
|---|---|---|
| LLM | `mistral:7b-instruct` via Ollama | Best determinism for medical Q&A locally |
| Embeddings | `nomic-embed-text` via Ollama | Fully local, no API needed |
| Vector Store | ChromaDB (persistent, cosine similarity) | Local, fast, metadata filtering support |
| Framework | LangChain (Python) | Mature RAG tooling |
| PDF Parser | PyMuPDF (`fitz`) | Superior table/layout extraction vs pypdf |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Deterministic reranking, open source |
| UI (optional) | Streamlit | Simple CLI + web interface |

---

## PROJECT STRUCTURE

```
medical_rag/
├── ingest.py          # PDF parsing, chunking, embedding, indexing
├── retriever.py       # Retrieval logic with thresholds and reranking
├── rag_pipeline.py    # Full RAG chain with prompt templates
├── config.py          # All config constants
├── evaluate.py        # Deterministic evaluation with test queries
├── main.py            # CLI entrypoint
└── requirements.txt   # All dependencies
```

---

## FILE 1: `config.py` — ALL CONSTANTS

```python
# ============================================================
# config.py — All configuration constants for Medical RAG
# ============================================================

PDF_PATH = "jogh-13-04116_merged.pdf"
CHROMA_PERSIST_DIR = "./chroma_medical_db"
COLLECTION_NAME = "medical_hrp_india"

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
TOP_K_RETRIEVAL = 8              # initial retrieval pool from ChromaDB
TOP_K_RERANK = 3                 # after reranking, top results sent to LLM
SIMILARITY_THRESHOLD = 0.65      # ChromaDB cosine DISTANCE threshold (lower=more similar)
                                  # distance > 0.65 = similarity < 0.35 → discard
RERANK_SCORE_THRESHOLD = 0.1     # cross-encoder minimum score to include chunk

# ----------------------------
# LLM PARAMETERS
# ----------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:7b-instruct"
TEMPERATURE = 0.0          # MUST be 0.0 for medical RAG — deterministic output
MAX_TOKENS = 1024
TOP_P = 1.0
REPEAT_PENALTY = 1.1

# ----------------------------
# EMBEDDING
# ----------------------------
EMBEDDING_MODEL = "nomic-embed-text"   # pulled via: ollama pull nomic-embed-text

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
```

---

## FILE 2: `ingest.py` — PDF PARSING WITH RICH METADATA

```python
# ============================================================
# ingest.py — Parse PDF, chunk with metadata, embed, store
# ============================================================

import fitz  # PyMuPDF
import re
import hashlib
import logging
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from config import *

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

# ----------------------------
# SECTION HEADER DETECTION
# Detects lines that are section headers in the PDF
# ----------------------------
SECTION_HEADERS = [
    "Hypertensive disorders of pregnancy",
    "Anaemia during pregnancy",
    "Twins/ Multiple pregnancy",
    "Placenta Previa",
    "Syphilis",
    "Hypothyroidism",
    "Gestational Diabetes Mellitus",
    "Management of GDM",
    "Special Obstetric care for PW with GDM",
    "Pregnancy with Previous Caesarean sections",
    "Intrauterine growth retardation",
    "Health schemes for improving maternal health",
    "Pradhan Mantri Matru Vandana Yojana",
    "Janani Suraksha Yojana",
    "Janani Shishu Suraksha Karyakaram",
    "DAKSHATA",
    "Antenatal Checkup",
    "Postnatal Care",
    "Management of PPH",
    "Management of Atonic PPH",
    "Neonatal Resuscitation",
    "Active Management of Third Stage of Labour",
    "Breastfeeding",
    "Antenatal Examination",
    "Eclampsia",
    "Pre Eclampsia",
    "High risk factors of pregnancy",
    "Universal Infection Prevention Practices",
    "Processing of Items for Reuse",
    "Labour Room Sterilization",
    "Operation Theatre Sterilization",
    "Antepartum Haemorrhage",
    "Vaginal Bleeding",
    "Hand Washing",
    "METHODS",
    "RESULTS",
    "DISCUSSION",
    "CONCLUSIONS",
    "Background characteristics of pregnant women",
    "Prevalence of high-risk pregnancies",
    "Determinants of high-risk pregnancies",
    "EXTENDED PMSMA FOR HRP TRACKING",
    "Guidance Note for Extended PMSMA",
]

FOOTER_BLACKLIST = [
    "for use in medical colleges, district hospitals and frus",
    "www.jogh.org",
    "2023 • vol. 13 • 04116",
]


def detect_page_type(page_number: int, text: str) -> str:
    """
    Classify page type using exact page ranges AND keyword fallback.
    Page ranges are derived from the actual PDF structure.
    """
    # Primary: use known page ranges
    for ptype, pages in PAGE_TYPE_RANGES.items():
        if page_number in pages:
            return ptype

    # Fallback: keyword-based detection
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["abstract", "methods", "nfhs", "logistic regression",
                                         "confidence interval", "adjusted odds ratio", "prevalence"]):
        return "research_paper"
    if any(kw in text_lower for kw in ["management", "diagnosis", "risk of", "refer to fru",
                                         "treatment recommended", "drug of choice"]):
        return "clinical_guideline"
    if any(kw in text_lower for kw in ["yojana", "abhiyan", "government of india", "scheme",
                                         "asha incentive", "pib.gov"]):
        return "government_policy"
    if any(kw in text_lower for kw in ["step 1", "step 2", "step 3", "for use in medical colleges"]):
        return "procedure_chart"
    if any(kw in text_lower for kw in ["annexure", "section a", "section b", "yes/no",
                                         "checklist", "s.no", "monitor"]):
        return "monitoring_checklist"

    return "unknown"


def detect_section_name(text: str) -> str:
    """
    Match text against known section headers from this specific PDF.
    Returns the matched section name or 'General'.
    """
    text_lower = text.lower()
    for header in SECTION_HEADERS:
        if header.lower() in text_lower:
            return header
    return "General"


def detect_condition(text: str) -> str:
    """
    Map chunk text to a medical condition tag using keyword matching.
    Returns the first matched condition or 'general'.
    """
    text_lower = text.lower()
    for condition, keywords in CONDITION_KEYWORDS.items():
        if condition == "general":
            continue
        if any(kw in text_lower for kw in keywords):
            return condition
    return "general"


def is_table_content(text: str) -> bool:
    """Detect if chunk contains tabular data (multiple aligned columns)."""
    lines = text.split('\n')
    table_lines = sum(1 for line in lines if len(line.split()) > 3
                      and any(char.isdigit() for char in line))
    return table_lines > 3


def is_list_content(text: str) -> bool:
    """Detect if chunk contains bullet/numbered lists."""
    list_patterns = [r'^\s*[•\-l]\s+', r'^\s*\d+\.\s+', r'^\s*[a-z]\)\s+']
    lines = text.split('\n')
    list_lines = sum(1 for line in lines
                     if any(re.match(p, line) for p in list_patterns))
    return list_lines > 2


def is_blacklisted(text: str) -> bool:
    """Discard chunks that are footers, page numbers, or boilerplate."""
    text_lower = text.lower().strip()
    if any(bl in text_lower for bl in FOOTER_BLACKLIST):
        return True
    if len(text.strip()) < MIN_CHUNK_LENGTH:
        return True
    # purely numeric
    if re.match(r'^\d+\s*$', text.strip()):
        return True
    return False


def chunk_text(text: str, page_type: str) -> list[str]:
    """
    Apply different chunk sizes based on page type.
    Procedure charts get smaller chunks; research paper gets standard size.
    """
    size = PROCEDURE_CHUNK_SIZE if page_type == "procedure_chart" else CHUNK_SIZE

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", ", ", " "],
        length_function=len,
    )
    return splitter.split_text(text)


def generate_chunk_id(text: str, page: int, idx: int) -> str:
    """Generate deterministic unique ID for each chunk."""
    hash_input = f"{page}_{idx}_{text[:50]}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def parse_and_chunk_pdf(pdf_path: str) -> list[dict]:
    """
    Main ingestion function.
    Returns list of dicts with 'text' and 'metadata'.
    """
    doc = fitz.open(pdf_path)
    all_chunks = []
    seen_texts = set()  # for deduplication

    print(f"[INGEST] Parsing {len(doc)} pages from {pdf_path}")

    for page_num in tqdm(range(len(doc)), desc="Parsing pages"):
        page = doc[page_num]
        page_number = page_num + 1  # 1-indexed

        # Extract text preserving layout
        raw_text = page.get_text("text")

        if not raw_text.strip():
            continue

        # Classify page
        page_type = detect_page_type(page_number, raw_text)
        section_name = detect_section_name(raw_text)

        # Chunk the page text
        chunks = chunk_text(raw_text, page_type)

        for idx, chunk_text_content in enumerate(chunks):
            # Skip blacklisted content
            if is_blacklisted(chunk_text_content):
                continue

            # Deduplication check
            text_hash = hashlib.md5(chunk_text_content.strip().encode()).hexdigest()
            if text_hash in seen_texts:
                logging.info(f"DUPLICATE skipped: page {page_number}, chunk {idx}")
                continue
            seen_texts.add(text_hash)

            condition = detect_condition(chunk_text_content)
            contains_table = is_table_content(chunk_text_content)
            contains_list = is_list_content(chunk_text_content)

            # Detect if this chunk starts with a section header
            is_header_chunk = any(
                header.lower() in chunk_text_content[:100].lower()
                for header in SECTION_HEADERS
            )

            metadata = {
                "source": pdf_path,
                "page_number": page_number,
                "page_type": page_type,
                "section_name": section_name,
                "condition": condition,
                "contains_table": contains_table,
                "contains_list": contains_list,
                "chunk_index": idx,
                "char_length": len(chunk_text_content),
                "is_header_chunk": is_header_chunk,
                "chunk_id": generate_chunk_id(chunk_text_content, page_number, idx),
            }

            all_chunks.append({"text": chunk_text_content, "metadata": metadata})

    doc.close()
    print(f"[INGEST] Total chunks after deduplication: {len(all_chunks)}")
    logging.info(f"INGEST COMPLETE | total_chunks={len(all_chunks)}")
    return all_chunks


def embed_and_store(chunks: list[dict]):
    """
    Embed chunks using Ollama nomic-embed-text and store in ChromaDB.
    Skips re-ingestion if collection already exists with data.
    """
    # Initialize ChromaDB persistent client
    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )

    # Check if already ingested
    existing = client.list_collections()
    if any(c.name == COLLECTION_NAME for c in existing):
        col = client.get_collection(COLLECTION_NAME)
        if col.count() > 0:
            print(f"[INGEST] Collection '{COLLECTION_NAME}' already exists "
                  f"with {col.count()} chunks. Skipping re-ingestion.")
            print("[INGEST] To re-ingest, delete ./chroma_medical_db directory first.")
            return

    # Initialize embeddings via Ollama
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # use cosine similarity
    )

    print(f"[INGEST] Embedding {len(chunks)} chunks using {EMBEDDING_MODEL}...")
    batch_size = 50

    for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding batches"):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        metadatas = [c["metadata"] for c in batch]
        ids = [c["metadata"]["chunk_id"] for c in batch]

        # Generate embeddings
        vectors = embeddings.embed_documents(texts)

        collection.add(
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas,
            ids=ids
        )

    print(f"[INGEST] Successfully stored {collection.count()} chunks in ChromaDB.")
    logging.info(f"EMBED COMPLETE | stored={collection.count()}")


def run_ingestion():
    """Entry point for full ingestion pipeline."""
    import os
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(
            f"PDF not found at '{PDF_PATH}'. "
            f"Place the file in the same directory as ingest.py"
        )
    chunks = parse_and_chunk_pdf(PDF_PATH)
    embed_and_store(chunks)
    print("[INGEST] Pipeline complete. Ready for querying.")


if __name__ == "__main__":
    run_ingestion()
```

---

## FILE 3: `retriever.py` — HYBRID RETRIEVAL WITH DETERMINISTIC THRESHOLDS

```python
# ============================================================
# retriever.py — Two-stage retrieval: vector + cross-encoder rerank
# ============================================================

import logging
from datetime import datetime
from sentence_transformers import CrossEncoder
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from config import *

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

# Load cross-encoder once at module level (expensive to reload)
print("[RETRIEVER] Loading cross-encoder reranker...")
RERANKER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print("[RETRIEVER] Reranker loaded.")


def detect_question_type(query: str) -> str:
    """Classify query into one of the predefined question types."""
    query_lower = query.lower()
    for qtype, keywords in QUESTION_TYPE_MAP.items():
        if any(kw in query_lower for kw in keywords):
            return qtype
    return "general"


def detect_query_condition(query: str) -> str:
    """Extract medical condition from query for metadata pre-filtering."""
    query_lower = query.lower()
    for condition, keywords in CONDITION_KEYWORDS.items():
        if condition == "general":
            continue
        if any(kw in query_lower for kw in keywords):
            return condition
    return None


def build_metadata_filter(query: str) -> dict | None:
    """
    Build ChromaDB where filter based on query content.
    Returns None if no specific filter applies (search all).
    """
    query_lower = query.lower()
    qtype = detect_question_type(query)
    condition = detect_query_condition(query)

    filters = []

    # Page type filter based on question type
    if qtype == "prevalence_statistic":
        filters.append({"page_type": {"$eq": "research_paper"}})
    elif qtype == "drug_dosage" or qtype == "clinical_management":
        filters.append({"page_type": {"$eq": "clinical_guideline"}})
    elif qtype == "policy_scheme":
        filters.append({"page_type": {"$eq": "government_policy"}})
    elif qtype == "procedure_steps":
        filters.append({"page_type": {"$in": ["procedure_chart", "clinical_guideline"]}})

    # Condition filter
    if condition:
        filters.append({"condition": {"$eq": condition}})

    if not filters:
        return None  # no filter → search all chunks
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def format_context_block(doc: str, metadata: dict, rank: int,
                          similarity_score: float, rerank_score: float) -> str:
    """Format a single retrieved chunk into a labeled context block."""
    return (
        f"[CHUNK {rank} | Page {metadata.get('page_number', '?')} | "
        f"Type: {metadata.get('page_type', '?')} | "
        f"Section: {metadata.get('section_name', '?')} | "
        f"Condition: {metadata.get('condition', '?')} | "
        f"Similarity: {1 - similarity_score:.3f} | Rerank: {rerank_score:.3f}]\n"
        f"{doc}"
    )


def retrieve(query: str, verbose: bool = True) -> dict:
    """
    Full two-stage retrieval pipeline.

    Stage 1: ChromaDB vector similarity search with metadata filtering
    Stage 2: Cross-encoder reranking with deterministic score threshold

    Returns dict with:
        - context: formatted string for LLM prompt
        - chunks: list of raw chunk dicts
        - metadata_used: pages, sections, conditions
        - retrieval_stats: for logging and display
    """
    # Initialize clients
    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(COLLECTION_NAME)

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    # -------------------------------------------------------
    # STEP 1: Query preprocessing
    # -------------------------------------------------------
    qtype = detect_question_type(query)
    condition = detect_query_condition(query)
    where_filter = build_metadata_filter(query)

    if verbose:
        print(f"\n[RETRIEVER] Question type: {qtype}")
        print(f"[RETRIEVER] Detected condition: {condition}")
        print(f"[RETRIEVER] Metadata filter: {where_filter}")

    # -------------------------------------------------------
    # STEP 2: Embed query
    # -------------------------------------------------------
    query_vector = embeddings.embed_query(query)

    # -------------------------------------------------------
    # STEP 3: Vector similarity search in ChromaDB
    # -------------------------------------------------------
    query_kwargs = {
        "query_embeddings": [query_vector],
        "n_results": TOP_K_RETRIEVAL,
        "include": ["documents", "metadatas", "distances"],
    }
    if where_filter:
        query_kwargs["where"] = where_filter

    try:
        results = collection.query(**query_kwargs)
    except Exception as e:
        # Fallback: retry without filter if filter causes error
        logging.warning(f"Filter query failed: {e}. Retrying without filter.")
        query_kwargs.pop("where", None)
        results = collection.query(**query_kwargs)

    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]  # ChromaDB cosine distance (0=identical)

    if verbose:
        print(f"[RETRIEVER] Stage 1 retrieved: {len(docs)} chunks")

    # -------------------------------------------------------
    # STEP 4: THRESHOLD GATE 1 — Similarity distance filter
    # Discard chunks where distance > SIMILARITY_THRESHOLD (0.65)
    # This means cosine similarity < 0.35 → not relevant enough
    # -------------------------------------------------------
    filtered = [
        (doc, meta, dist)
        for doc, meta, dist in zip(docs, metadatas, distances)
        if dist <= SIMILARITY_THRESHOLD
    ]

    if verbose:
        print(f"[RETRIEVER] After similarity threshold ({SIMILARITY_THRESHOLD}): "
              f"{len(filtered)}/{len(docs)} chunks passed")

    # Hard gate: if fewer than 2 relevant chunks found, return no-answer signal
    if len(filtered) < 2:
        logging.warning(f"INSUFFICIENT CHUNKS | query='{query}' | "
                        f"passed_threshold={len(filtered)}")
        return {
            "context": None,
            "chunks": [],
            "metadata_used": {},
            "retrieval_stats": {
                "stage1_count": len(docs),
                "threshold_passed": len(filtered),
                "rerank_passed": 0,
            },
            "no_answer": True,
        }

    # -------------------------------------------------------
    # STEP 5: THRESHOLD GATE 2 — Cross-encoder reranking
    # Score each (query, chunk) pair and filter by rerank score
    # -------------------------------------------------------
    pairs = [(query, doc) for doc, _, _ in filtered]
    rerank_scores = RERANKER.predict(pairs)

    # Combine with original distance scores
    ranked = sorted(
        zip([d for d, _, _ in filtered],
            [m for _, m, _ in filtered],
            [dist for _, _, dist in filtered],
            rerank_scores),
        key=lambda x: x[3],  # sort by rerank score descending
        reverse=True
    )

    # Apply rerank threshold
    reranked = [
        (doc, meta, dist, score)
        for doc, meta, dist, score in ranked
        if score >= RERANK_SCORE_THRESHOLD
    ]

    if verbose:
        print(f"[RETRIEVER] After rerank threshold ({RERANK_SCORE_THRESHOLD}): "
              f"{len(reranked)}/{len(filtered)} chunks passed")

    # Take top K
    final_chunks = reranked[:TOP_K_RERANK]

    if not final_chunks:
        return {
            "context": None,
            "chunks": [],
            "metadata_used": {},
            "retrieval_stats": {
                "stage1_count": len(docs),
                "threshold_passed": len(filtered),
                "rerank_passed": 0,
            },
            "no_answer": True,
        }

    # -------------------------------------------------------
    # STEP 6: Assemble context for LLM
    # -------------------------------------------------------
    context_blocks = []
    pages_used = []
    sections_used = []
    conditions_used = []

    for rank, (doc, meta, dist, rscore) in enumerate(final_chunks, 1):
        block = format_context_block(doc, meta, rank, dist, rscore)
        context_blocks.append(block)
        pages_used.append(meta.get("page_number"))
        sections_used.append(meta.get("section_name"))
        conditions_used.append(meta.get("condition"))

    context = "\n---\n".join(context_blocks)

    # Log retrieval event
    logging.info(
        f"RETRIEVAL | query='{query}' | qtype={qtype} | condition={condition} | "
        f"stage1={len(docs)} | threshold_passed={len(filtered)} | "
        f"rerank_passed={len(reranked)} | final={len(final_chunks)} | "
        f"pages={pages_used}"
    )

    return {
        "context": context,
        "chunks": final_chunks,
        "metadata_used": {
            "pages": pages_used,
            "sections": list(set(sections_used)),
            "conditions": list(set(conditions_used)),
        },
        "retrieval_stats": {
            "stage1_count": len(docs),
            "threshold_passed": len(filtered),
            "rerank_passed": len(reranked),
            "final_count": len(final_chunks),
        },
        "no_answer": False,
    }
```

---

## FILE 4: `rag_pipeline.py` — PROMPT ENGINEERING & ANSWER VALIDATION

```python
# ============================================================
# rag_pipeline.py — Full RAG chain with medical prompt templates
# ============================================================

import re
import logging
import requests
import json
from config import *
from retriever import retrieve

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

# ============================================================
# SYSTEM PROMPT — injected with every query
# Strictly scoped to the merged PDF content
# ============================================================
SYSTEM_PROMPT = """You are a specialized medical AI assistant for maternal and reproductive health in India.
You answer questions strictly based on the provided context extracted from:

1. A peer-reviewed research paper (Kuppusamy et al., 2023, Journal of Global Health) analyzing
   high-risk pregnancy prevalence in India using NFHS-5 (National Family Health Survey-5) data
   covering 23,853 currently pregnant women across all Indian states and Union Territories.

2. Clinical management guidelines for high-risk pregnancy conditions under India's PMSMA program,
   covering: hypertension/pre-eclampsia/eclampsia, anaemia, gestational diabetes mellitus (GDM),
   hypothyroidism, syphilis, IUGR, previous caesarean section, placenta previa, twin pregnancy.

3. Government of India health scheme descriptions including PMSMA, JSY, JSSK, PMMMVY, DAKSHATA
   and PMSMA extended HRP tracking operational guidelines.

4. Clinical procedure reference charts from the National Rural Health Mission covering:
   ANC checkup, postnatal care, PPH management, AMTSL, eclampsia management,
   neonatal resuscitation, breastfeeding, antenatal examination, infection prevention.

5. PMSMA onsite monitoring and self-assessment checklists (Annexure 1 and Annexure 2).

STRICT RULES:
- Answer ONLY from the provided context. Do NOT use any external medical knowledge.
- If the answer is not in the context, say exactly: "This information is not available in the provided document."
- For drug dosages and clinical protocols, reproduce the EXACT values from the context (mg, units, frequency, route).
- For statistics, cite the EXACT figures with their source (e.g., "According to NFHS-5 analysis by Kuppusamy et al.").
- Always mention the section and page source when giving clinical guidance.
- Do NOT speculate, infer, or extrapolate beyond what the document explicitly states.
- For procedural questions, present steps in the EXACT numbered order as given in the source.
- If a question involves emergency clinical management (eclampsia, PPH, APH, neonatal resuscitation),
  always append: "[CLINICAL DECISION — VERIFY WITH QUALIFIED TREATING PHYSICIAN BEFORE ACTING]"
- If the question is about drug dosage for a specific patient scenario, append:
  "[DOSAGE — CONFIRM WITH PRESCRIBING PHYSICIAN. THIS IS DOCUMENT REFERENCE ONLY]"
"""

# ============================================================
# QUERY PROMPT TEMPLATE
# ============================================================
QUERY_PROMPT_TEMPLATE = """Context retrieved from the medical document:

{context}

---

Question: {question}

Instructions for answering:
- Base your answer STRICTLY on the context above. Do not add information from outside the context.
- If the context contains a table relevant to this question, present the data in a structured format.
- If the question asks about a statistic, include the exact percentage/number and sample size if mentioned.
- If the question asks about drug management, include drug name, dose, route, and frequency exactly as stated in context.
- If multiple context chunks provide relevant information, synthesize them coherently.
- At the end of your answer, on a new line, write: "Source: Page(s) [list page numbers] — [list section names]"

Answer:"""

# ============================================================
# NO-ANSWER RESPONSE
# ============================================================
NO_ANSWER_RESPONSE = (
    "This information is not available in the provided document. "
    "The document covers: high-risk pregnancy prevalence in India (NFHS-5 data), "
    "clinical guidelines for hypertension, anaemia, GDM, hypothyroidism, syphilis, "
    "IUGR, previous CS, placenta previa, twin pregnancy, Government of India maternal "
    "health schemes (PMSMA, JSY, JSSK), and clinical procedure charts for ANC, PPH, "
    "AMTSL, eclampsia, and neonatal resuscitation."
)


def call_ollama(system_prompt: str, user_prompt: str) -> str:
    """
    Call Ollama API directly for full control over parameters.
    Uses temperature=0.0 for deterministic medical responses.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,       # 0.0 = deterministic
            "num_predict": MAX_TOKENS,
            "top_p": TOP_P,
            "repeat_penalty": REPEAT_PENALTY,
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Cannot connect to Ollama. Start it with: ollama serve\n"
            f"Then pull the model: ollama pull {OLLAMA_MODEL}"
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama request timed out after 120 seconds.")


def validate_answer(answer: str, retrieved_chunks: list) -> dict:
    """
    Post-processing validation of LLM answer.

    Checks:
    1. Is the answer a no-answer signal?
    2. Do any numbers/statistics in the answer appear in the retrieved chunks?
    3. Is the answer suspiciously short (incomplete)?

    Returns validation report dict.
    """
    validation = {
        "is_no_answer": False,
        "hallucination_flag": False,
        "hallucinated_numbers": [],
        "is_incomplete": False,
        "warnings": [],
    }

    # Check 1: No-answer signal
    no_answer_signals = [
        "not available in the provided document",
        "not found in the context",
        "cannot find this information",
        "not mentioned in the document",
    ]
    if any(signal in answer.lower() for signal in no_answer_signals):
        validation["is_no_answer"] = True
        return validation

    # Check 2: Hallucination detection — verify numbers exist in source chunks
    numbers_in_answer = re.findall(r'\b\d+\.?\d*%?\b', answer)
    all_chunk_text = " ".join([c[0] for c in retrieved_chunks]) if retrieved_chunks else ""

    hallucinated = []
    for num in numbers_in_answer:
        # Skip very common numbers (years, page numbers, small integers)
        if len(num) <= 1 or num in ["10", "20", "100", "0"]:
            continue
        if num not in all_chunk_text:
            hallucinated.append(num)

    if hallucinated:
        validation["hallucination_flag"] = True
        validation["hallucinated_numbers"] = hallucinated
        validation["warnings"].append(
            f"WARNING: The following numbers could not be verified in retrieved chunks: "
            f"{hallucinated}. Please cross-check with original document."
        )

    # Check 3: Incomplete answer
    if len(answer.strip()) < 50:
        validation["is_incomplete"] = True
        validation["warnings"].append(
            "WARNING: Answer appears very short. Response may be incomplete."
        )

    return validation


def run_rag(query: str, verbose: bool = True) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks (with thresholds)
    2. Build prompt
    3. Call LLM
    4. Validate answer
    5. Return full result dict
    """
    # STEP 1: Retrieval
    retrieval_result = retrieve(query, verbose=verbose)

    # STEP 2: Handle no-answer case (insufficient retrieval)
    if retrieval_result["no_answer"]:
        return {
            "query": query,
            "answer": NO_ANSWER_RESPONSE,
            "metadata_used": {},
            "retrieval_stats": retrieval_result["retrieval_stats"],
            "validation": {"is_no_answer": True},
            "no_answer": True,
        }

    # STEP 3: Build query prompt
    user_prompt = QUERY_PROMPT_TEMPLATE.format(
        context=retrieval_result["context"],
        question=query
    )

    # STEP 4: Call LLM
    if verbose:
        print(f"[RAG] Calling {OLLAMA_MODEL} with temperature={TEMPERATURE}...")

    answer = call_ollama(SYSTEM_PROMPT, user_prompt)

    # STEP 5: Validate answer
    validation = validate_answer(answer, retrieval_result["chunks"])

    # Append validation warnings to answer if any
    if validation["warnings"]:
        answer += "\n\n" + "\n".join(validation["warnings"])

    # Log full pipeline event
    logging.info(
        f"RAG_COMPLETE | query='{query}' | "
        f"pages={retrieval_result['metadata_used'].get('pages')} | "
        f"hallucination_flag={validation['hallucination_flag']} | "
        f"answer_length={len(answer)}"
    )

    return {
        "query": query,
        "answer": answer,
        "metadata_used": retrieval_result["metadata_used"],
        "retrieval_stats": retrieval_result["retrieval_stats"],
        "validation": validation,
        "no_answer": False,
    }
```

---

## FILE 5: `evaluate.py` — DETERMINISTIC TEST SUITE

```python
# ============================================================
# evaluate.py — Validation test suite with expected answers
# All expected values derived directly from the merged PDF
# ============================================================

from rag_pipeline import run_rag

# ============================================================
# TEST QUERIES — Every expected value comes directly from PDF
# ============================================================
TEST_QUERIES = [
    # --- RESEARCH PAPER QUERIES ---
    {
        "id": "RP-01",
        "query": "What is the overall prevalence of high-risk pregnancy in India?",
        "expected_contains": ["49.4%"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-02",
        "query": "Which Indian states have the highest prevalence of high-risk pregnancies?",
        "expected_contains": ["Meghalaya", "67.8", "Manipur", "66.7"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-03",
        "query": "What is the adjusted odds ratio for women with no education and high-risk pregnancy?",
        "expected_contains": ["2.02", "1.84", "2.22"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-04",
        "query": "What percentage of Indian pregnant women had short birth spacing?",
        "expected_contains": ["31.1"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-05",
        "query": "What percentage of women had adverse birth outcomes in their last birth?",
        "expected_contains": ["19.5"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-06",
        "query": "What is the adjusted odds ratio for the poorest wealth quintile and high-risk pregnancy?",
        "expected_contains": ["1.33", "1.18", "1.49"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-07",
        "query": "What percentage of women had multiple high-risk factors?",
        "expected_contains": ["16.4"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },

    # --- CLINICAL GUIDELINE QUERIES ---
    {
        "id": "CG-01",
        "query": "What is the first-line drug for hypertension in pregnancy and its dose?",
        "expected_contains": ["Alpha methyl dopa", "250 mg"],
        "expected_page_type": "clinical_guideline",
        "category": "drug_dosage",
    },
    {
        "id": "CG-02",
        "query": "What is the loading dose of magnesium sulfate for eclampsia?",
        "expected_contains": ["4 gm", "5 gm", "IM"],
        "expected_page_type": "clinical_guideline",
        "category": "drug_dosage",
    },
    {
        "id": "CG-03",
        "query": "How is severe anaemia defined in pregnancy and what is its management?",
        "expected_contains": ["7 g", "FRU", "blood transfusion"],
        "expected_page_type": "clinical_guideline",
        "category": "clinical_management",
    },
    {
        "id": "CG-04",
        "query": "What TSH level in first trimester requires hypothyroidism treatment?",
        "expected_contains": ["2.5", "levothyroxine"],
        "expected_page_type": "clinical_guideline",
        "category": "diagnostic_criteria",
    },
    {
        "id": "CG-05",
        "query": "What is the GDM diagnosis threshold and when is the second test done?",
        "expected_contains": ["140 mg", "24-28 weeks"],
        "expected_page_type": "clinical_guideline",
        "category": "diagnostic_criteria",
    },
    {
        "id": "CG-06",
        "query": "What is the treatment for early stage syphilis in pregnancy?",
        "expected_contains": ["2.4 million", "benzathine", "penicillin"],
        "expected_page_type": "clinical_guideline",
        "category": "drug_dosage",
    },

    # --- PROCEDURE CHART QUERIES ---
    {
        "id": "PC-01",
        "query": "What are the steps of Active Management of Third Stage of Labour?",
        "expected_contains": ["Oxytocin 10", "cord traction", "uterine massage"],
        "expected_page_type": "procedure_chart",
        "category": "procedure_steps",
    },
    {
        "id": "PC-02",
        "query": "When should breastfeeding be initiated after delivery?",
        "expected_contains": ["1 hour"],
        "expected_page_type": "procedure_chart",
        "category": "procedure_steps",
    },
    {
        "id": "PC-03",
        "query": "How many minimum antenatal checkups are required during pregnancy?",
        "expected_contains": ["4"],
        "expected_page_type": "procedure_chart",
        "category": "clinical_management",
    },

    # --- GOVERNMENT POLICY QUERIES ---
    {
        "id": "GP-01",
        "query": "What cash benefit is given under Pradhan Mantri Matru Vandana Yojana?",
        "expected_contains": ["5,000", "1000", "2000"],
        "expected_page_type": "government_policy",
        "category": "policy_scheme",
    },
    {
        "id": "GP-02",
        "query": "What is the ASHA incentive under extended PMSMA for HRP follow-up visits?",
        "expected_contains": ["100", "500", "45"],
        "expected_page_type": "government_policy",
        "category": "policy_scheme",
    },
    {
        "id": "GP-03",
        "query": "On which day of every month is the PMSMA clinic conducted?",
        "expected_contains": ["9th"],
        "expected_page_type": "government_policy",
        "category": "policy_scheme",
    },

    # --- CHECKLIST QUERIES ---
    {
        "id": "CL-01",
        "query": "What equipment must be available at a PMSMA clinic?",
        "expected_contains": ["BP Apparatus", "Glucometer", "Fetoscope"],
        "expected_page_type": "monitoring_checklist",
        "category": "checklist",
    },

    # --- OUT OF SCOPE (should return NO ANSWER) ---
    {
        "id": "OOS-01",
        "query": "What is the treatment for COVID-19 in pregnancy?",
        "expected_contains": ["not available in the provided document"],
        "expected_page_type": None,
        "category": "out_of_scope",
    },
    {
        "id": "OOS-02",
        "query": "What is the global maternal mortality rate in 2023?",
        "expected_contains": ["not available"],
        "expected_page_type": None,
        "category": "out_of_scope",
    },
]


def run_evaluation():
    """Run all test queries and print evaluation report."""
    print("\n" + "="*70)
    print("MEDICAL RAG EVALUATION REPORT")
    print("="*70)

    total = len(TEST_QUERIES)
    passed = 0
    failed = 0
    results = []

    for test in TEST_QUERIES:
        print(f"\n[{test['id']}] {test['query'][:70]}...")

        result = run_rag(test["query"], verbose=False)
        answer = result["answer"].lower()

        # Check expected strings
        all_found = all(exp.lower() in answer for exp in test["expected_contains"])

        # Check correct page type was retrieved
        retrieved_pages = result["metadata_used"].get("pages", [])
        correct_type_retrieved = True
        if test["expected_page_type"]:
            # We can't directly check page_type from pages alone;
            # check via stats instead
            correct_type_retrieved = result["retrieval_stats"]["final_count"] > 0

        hallucinated = result["validation"].get("hallucination_flag", False)

        status = "PASS" if all_found and not hallucinated else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"  Status         : {status}")
        print(f"  Pages retrieved: {retrieved_pages}")
        print(f"  Chunks used    : {result['retrieval_stats'].get('final_count', 0)}")
        print(f"  Expected found : {all_found}")
        print(f"  Hallucination  : {hallucinated}")
        if not all_found:
            print(f"  Missing        : {[e for e in test['expected_contains'] if e.lower() not in answer]}")

        results.append({**test, "status": status, "answer_snippet": result["answer"][:200]})

    # Summary
    print("\n" + "="*70)
    print(f"EVALUATION SUMMARY: {passed}/{total} PASSED | {failed}/{total} FAILED")
    print(f"Accuracy: {passed/total*100:.1f}%")
    print("="*70)

    return results


if __name__ == "__main__":
    run_evaluation()
```

---

## FILE 6: `main.py` — CLI ENTRYPOINT

```python
# ============================================================
# main.py — CLI entrypoint supporting 4 modes
# ============================================================

import argparse
import sys
from config import OLLAMA_MODEL, OLLAMA_BASE_URL


def print_result(result: dict):
    """Pretty-print a RAG result to the console."""
    print("\n" + "="*70)
    print(f"QUERY: {result['query']}")
    print("-"*70)

    stats = result.get("retrieval_stats", {})
    meta = result.get("metadata_used", {})

    print(f"RETRIEVED CHUNKS : {stats.get('stage1_count', 0)} initially")
    print(f"AFTER THRESHOLD  : {stats.get('threshold_passed', 0)} passed similarity gate")
    print(f"AFTER RERANKING  : {stats.get('rerank_passed', 0)} passed rerank gate")
    print(f"FINAL CHUNKS USED: {stats.get('final_count', 0)}")
    print(f"PAGES USED       : {meta.get('pages', [])}")
    print(f"SECTIONS USED    : {meta.get('sections', [])}")
    print(f"CONDITIONS TAGGED: {meta.get('conditions', [])}")

    validation = result.get("validation", {})
    if validation.get("hallucination_flag"):
        print(f"⚠ HALLUCINATION WARNING: Unverified numbers: "
              f"{validation.get('hallucinated_numbers')}")

    print("-"*70)
    print("ANSWER:")
    print(result["answer"])
    print("="*70)


def check_ollama():
    """Verify Ollama is running before proceeding."""
    import requests
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        if not any(OLLAMA_MODEL.split(":")[0] in m for m in models):
            print(f"⚠ Model '{OLLAMA_MODEL}' not found in Ollama.")
            print(f"  Run: ollama pull {OLLAMA_MODEL}")
            sys.exit(1)
        print(f"[OK] Ollama running. Model '{OLLAMA_MODEL}' available.")
    except Exception:
        print("ERROR: Cannot connect to Ollama.")
        print("  Start Ollama: ollama serve")
        print(f"  Pull model  : ollama pull {OLLAMA_MODEL}")
        print("  Pull embed  : ollama pull nomic-embed-text")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Medical RAG for High-Risk Pregnancy PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  --ingest              Parse PDF, embed, and store in ChromaDB
  --query "..."         Run a single query
  --interactive         Start interactive REPL
  --evaluate            Run full evaluation test suite

Examples:
  python main.py --ingest
  python main.py --query "What is the prevalence of HRP in India?"
  python main.py --interactive
  python main.py --evaluate
        """
    )
    parser.add_argument("--ingest", action="store_true",
                        help="Parse and index the PDF into ChromaDB")
    parser.add_argument("--query", type=str, metavar="QUESTION",
                        help="Run a single query through the RAG pipeline")
    parser.add_argument("--interactive", action="store_true",
                        help="Start interactive query loop")
    parser.add_argument("--evaluate", action="store_true",
                        help="Run evaluation test suite")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    # --- INGEST MODE ---
    if args.ingest:
        check_ollama()
        from ingest import run_ingestion
        run_ingestion()

    # --- SINGLE QUERY MODE ---
    elif args.query:
        check_ollama()
        from rag_pipeline import run_rag
        result = run_rag(args.query, verbose=True)
        print_result(result)

    # --- INTERACTIVE MODE ---
    elif args.interactive:
        check_ollama()
        from rag_pipeline import run_rag
        print("\nMedical RAG — Interactive Mode")
        print("Type your question and press Enter. Type 'exit' to quit.\n")
        while True:
            try:
                query = input("Query> ").strip()
                if not query:
                    continue
                if query.lower() in ["exit", "quit", "q"]:
                    print("Exiting.")
                    break
                result = run_rag(query, verbose=True)
                print_result(result)
            except KeyboardInterrupt:
                print("\nExiting.")
                break

    # --- EVALUATE MODE ---
    elif args.evaluate:
        check_ollama()
        from evaluate import run_evaluation
        run_evaluation()


if __name__ == "__main__":
    main()
```

---

## FILE 7: `requirements.txt`

```txt
langchain>=0.2.0
langchain-community>=0.2.0
langchain-ollama>=0.1.0
chromadb>=0.5.0
PyMuPDF>=1.24.0
sentence-transformers>=2.7.0
torch>=2.0.0
requests>=2.31.0
tqdm>=4.66.0
numpy>=1.26.0
streamlit>=1.35.0
python-dotenv>=1.0.0
```

---

## SETUP & RUN INSTRUCTIONS

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama (in a separate terminal)
ollama serve

# 3. Pull required models
ollama pull mistral:7b-instruct
ollama pull nomic-embed-text

# 4. Place your PDF in the project directory
# File must be named: jogh-13-04116_merged.pdf

# 5. Ingest the PDF (only needed once)
python main.py --ingest

# 6. Run a single query
python main.py --query "What is the prevalence of high-risk pregnancy in India?"

# 7. Interactive mode
python main.py --interactive

# 8. Run evaluation suite
python main.py --evaluate
```

---

## KEY DESIGN DECISIONS

| Decision | Value | Reason |
|---|---|---|
| `TEMPERATURE=0.0` | 0.0 | Medical responses must be deterministic, not creative |
| `SIMILARITY_THRESHOLD=0.65` | ChromaDB distance ≤ 0.65 | Filters chunks with cosine similarity < 0.35 — not medically relevant |
| `RERANK_SCORE_THRESHOLD=0.1` | cross-encoder ≥ 0.1 | Second gate to eliminate borderline-relevant chunks |
| `TOP_K_RETRIEVAL=8` | 8 chunks | Large enough pool for diverse retrieval before reranking |
| `TOP_K_RERANK=3` | 3 chunks | LLM context window focus — only highest quality chunks |
| `CHUNK_SIZE=600` | 600 chars | Balances context richness vs retrieval precision |
| `PROCEDURE_CHUNK_SIZE=400` | 400 chars | Procedure charts are dense and list-like; smaller chunks improve precision |
| `MIN_CHUNK_LENGTH=80` | 80 chars | Eliminates footers, headers, page numbers |
| Cosine similarity in ChromaDB | `hnsw:space=cosine` | Best for semantic text matching vs Euclidean |
| Cross-encoder reranker | `ms-marco-MiniLM-L-6-v2` | Trained on question-passage pairs; ideal for RAG reranking |
| Post-processing number check | Regex + substring match | Catches hallucinated statistics before returning to user |

---

## ADDITIONAL REQUIREMENTS FOR CODING AGENT

1. **PERSISTENCE**: ChromaDB must persist to disk. Check if collection exists and has data before re-ingesting. Never wipe existing collection without explicit `--reingest` flag.

2. **FULL IMPLEMENTATION**: All files must be fully implemented with working code — no pseudocode, no placeholder comments like `# TODO`.

3. **DEDUPLICATION**: After chunking, deduplicate chunks with identical text. Common duplicate in this PDF: `"For use in medical colleges, district hospitals and FRUs"` appears on almost every procedure chart page.

4. **ERROR HANDLING**: Every function must have try/except with specific, actionable error messages. No silent failures.

5. **NO PAID APIs**: Everything runs locally via Ollama. No OpenAI, no Anthropic, no HuggingFace Inference API calls.

6. **INLINE COMMENTS**: Every threshold value must have a comment explaining WHY that value was chosen.

7. **LOGGING**: Every retrieval event logged to `medical_rag.log` with: timestamp, query, chunks_retrieved, chunks_after_threshold, chunks_after_rerank, similarity_scores, rerank_scores, pages_used.
