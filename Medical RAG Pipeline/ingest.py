# ============================================================
# ingest.py — Parse PDF, chunk with metadata, embed, store
# ============================================================

import fitz  # PyMuPDF
import re
import hashlib
import logging
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
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
    for ptype, pages in PAGE_TYPE_RANGES.items():
        if page_number in pages:
            return ptype

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

        raw_text = page.get_text("text")

        if not raw_text.strip():
            continue

        page_type = detect_page_type(page_number, raw_text)
        section_name = detect_section_name(raw_text)

        chunks = chunk_text(raw_text, page_type)

        for idx, chunk_text_content in enumerate(chunks):
            if is_blacklisted(chunk_text_content):
                continue

            text_hash = hashlib.md5(chunk_text_content.strip().encode()).hexdigest()
            if text_hash in seen_texts:
                logging.info(f"DUPLICATE skipped: page {page_number}, chunk {idx}")
                continue
            seen_texts.add(text_hash)

            condition = detect_condition(chunk_text_content)
            contains_table = is_table_content(chunk_text_content)
            contains_list = is_list_content(chunk_text_content)

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
    Embed chunks using OpenAI text-embedding-3-small and store in FAISS.
    Skips re-ingestion if index already exists on disk.
    """
    import os
    if os.path.exists(os.path.join(FAISS_INDEX_DIR, "index.faiss")):
        print(f"[INGEST] FAISS index already exists at '{FAISS_INDEX_DIR}'. "
              f"Skipping re-ingestion.")
        print(f"[INGEST] To re-ingest, delete the '{FAISS_INDEX_DIR}' directory first.")
        return

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    documents = [
        Document(page_content=c["text"], metadata=c["metadata"])
        for c in chunks
    ]

    print(f"[INGEST] Embedding {len(documents)} chunks using {EMBEDDING_MODEL}...")

    batch_size = 50
    vectorstore = None

    for i in tqdm(range(0, len(documents), batch_size), desc="Embedding batches"):
        batch = documents[i:i + batch_size]
        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            batch_store = FAISS.from_documents(batch, embeddings)
            vectorstore.merge_from(batch_store)

    vectorstore.save_local(FAISS_INDEX_DIR)
    print(f"[INGEST] Successfully stored {len(documents)} chunks in FAISS at '{FAISS_INDEX_DIR}'.")
    logging.info(f"EMBED COMPLETE | stored={len(documents)}")


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
