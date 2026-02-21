# ============================================================
# retriever.py — Two-stage retrieval: vector + cross-encoder rerank
# ============================================================

import re
import logging
from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from config import *

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

# Load cross-encoder once at module level (expensive to reload)
print("[RETRIEVER] Loading cross-encoder reranker...")
RERANKER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print("[RETRIEVER] Reranker loaded.")


def normalize_query(query: str) -> str:
    """
    Normalize query by expanding colloquial terms, age references,
    and abbreviations into medical terminology.
    This dramatically improves FAISS embedding similarity matching.
    """
    normalized = query

    for rule in QUERY_NORMALIZATION_RULES["age_patterns"]:
        match = re.search(rule["pattern"], normalized, re.IGNORECASE)
        if match:
            normalized = normalized + " " + rule["replacement"]

    query_lower = normalized.lower()
    for abbrev, expansion in QUERY_NORMALIZATION_RULES["abbreviation_map"].items():
        if abbrev in query_lower:
            normalized = normalized + " " + expansion

    for term, expansion in QUERY_NORMALIZATION_RULES["clinical_synonyms"].items():
        if term.lower() in query_lower:
            normalized = normalized + " " + expansion

    return normalized


def extract_keywords_from_query(query: str) -> list[str]:
    """
    Extract relevant keyword groups from the query for hybrid keyword search.
    Returns a flat list of keywords to search for in document text.
    """
    query_lower = query.lower()
    matched_keywords = []

    for group, terms in KEYWORD_SEARCH_TERMS.items():
        if any(t.lower() in query_lower for t in terms) or group in query_lower:
            matched_keywords.extend(terms)

    for condition, keywords in CONDITION_KEYWORDS.items():
        if condition == "general":
            continue
        if any(kw in query_lower for kw in keywords):
            matched_keywords.extend(keywords)

    return list(set(matched_keywords))


def keyword_search(vectorstore: FAISS, query: str, max_results: int) -> list:
    """
    Keyword-based fallback search through FAISS docstore.
    Scores documents by number of keyword matches.
    Returns list of (Document, keyword_score) tuples.
    """
    keywords = extract_keywords_from_query(query)
    if not keywords:
        return []

    query_words = set(query.lower().split())
    keywords_set = set(kw.lower() for kw in keywords)
    all_search_terms = keywords_set | query_words

    scored_docs = []
    docstore = vectorstore.docstore._dict

    for doc_id, doc in docstore.items():
        text_lower = doc.page_content.lower()
        match_count = sum(1 for term in all_search_terms if term in text_lower)
        if match_count >= 2:
            scored_docs.append((doc, match_count))

    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return scored_docs[:max_results]


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


def get_expected_page_type(qtype: str) -> list[str] | None:
    """
    Map question type to expected page types for post-retrieval filtering.
    Returns None if no specific filter applies (search all).
    """
    if qtype == "prevalence_statistic":
        return ["research_paper"]
    elif qtype in ("drug_dosage", "clinical_management"):
        return ["clinical_guideline"]
    elif qtype == "policy_scheme":
        return ["government_policy"]
    elif qtype == "procedure_steps":
        return ["procedure_chart", "clinical_guideline"]
    return None


def apply_metadata_filter(docs_and_scores: list, expected_page_types: list[str] | None,
                           condition: str | None) -> list:
    """
    Post-retrieval metadata filtering for FAISS results.
    Falls back to unfiltered results if filtering yields too few chunks.
    """
    if not expected_page_types and not condition:
        return docs_and_scores

    filtered = []
    for doc, score in docs_and_scores:
        meta = doc.metadata
        type_match = (expected_page_types is None or
                      meta.get("page_type") in expected_page_types)
        cond_match = (condition is None or
                      meta.get("condition") == condition)
        if type_match and cond_match:
            filtered.append((doc, score))

    if len(filtered) >= 2:
        return filtered

    soft_filtered = []
    for doc, score in docs_and_scores:
        meta = doc.metadata
        type_match = (expected_page_types is None or
                      meta.get("page_type") in expected_page_types)
        cond_match = (condition is None or
                      meta.get("condition") == condition)
        if type_match or cond_match:
            soft_filtered.append((doc, score))

    if len(soft_filtered) >= 2:
        return soft_filtered

    return docs_and_scores


def format_context_block(doc_text: str, metadata: dict, rank: int,
                          l2_score: float, rerank_score: float) -> str:
    """Format a single retrieved chunk into a labeled context block."""
    return (
        f"[CHUNK {rank} | Page {metadata.get('page_number', '?')} | "
        f"Type: {metadata.get('page_type', '?')} | "
        f"Section: {metadata.get('section_name', '?')} | "
        f"Condition: {metadata.get('condition', '?')} | "
        f"L2 Dist: {l2_score:.3f} | Rerank: {rerank_score:.3f}]\n"
        f"{doc_text}"
    )


def retrieve(query: str, verbose: bool = True) -> dict:
    """
    Full two-stage retrieval pipeline.

    Stage 1: FAISS vector similarity search with post-retrieval metadata filtering
    Stage 2: Cross-encoder reranking with deterministic score threshold

    Returns dict with:
        - context: formatted string for LLM prompt
        - chunks: list of raw chunk dicts
        - metadata_used: pages, sections, conditions
        - retrieval_stats: for logging and display
    """
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    vectorstore = FAISS.load_local(
        FAISS_INDEX_DIR, embeddings,
        allow_dangerous_deserialization=True
    )

    # STEP 1: Query preprocessing + normalization
    qtype = detect_question_type(query)
    condition = detect_query_condition(query)
    expected_page_types = get_expected_page_type(qtype)

    normalized_query = normalize_query(query)
    query_was_normalized = normalized_query != query

    if verbose:
        print(f"\n[RETRIEVER] Question type: {qtype}")
        print(f"[RETRIEVER] Detected condition: {condition}")
        print(f"[RETRIEVER] Expected page types: {expected_page_types}")
        if query_was_normalized:
            print(f"[RETRIEVER] Normalized query: {normalized_query[:120]}...")

    # STEP 2a: Broad FAISS similarity search (using normalized query)
    docs_and_scores = vectorstore.similarity_search_with_score(normalized_query, k=FAISS_FETCH_K)

    if verbose:
        print(f"[RETRIEVER] Stage 1 FAISS fetched: {len(docs_and_scores)} chunks")

    # STEP 2b: Hybrid keyword search fallback
    keyword_results = keyword_search(vectorstore, query, max_results=KEYWORD_MATCH_BOOST * 3)

    seen_contents = set(doc.page_content[:100] for doc, _ in docs_and_scores)
    keyword_injected = 0
    for kw_doc, kw_score in keyword_results:
        if kw_doc.page_content[:100] not in seen_contents and keyword_injected < KEYWORD_MATCH_BOOST:
            docs_and_scores.append((kw_doc, SIMILARITY_THRESHOLD * 0.8))
            seen_contents.add(kw_doc.page_content[:100])
            keyword_injected += 1

    if verbose and keyword_injected > 0:
        print(f"[RETRIEVER] Hybrid: injected {keyword_injected} keyword-matched chunks")

    # STEP 3: Post-retrieval metadata filtering
    filtered_docs = apply_metadata_filter(docs_and_scores, expected_page_types, condition)

    # Take top TOP_K_RETRIEVAL after metadata filter
    filtered_docs = filtered_docs[:TOP_K_RETRIEVAL]

    if verbose:
        print(f"[RETRIEVER] After metadata filter: {len(filtered_docs)} chunks")

    # STEP 4: THRESHOLD GATE 1 — L2 distance filter (soft gate)
    threshold_passed = [
        (doc, score)
        for doc, score in filtered_docs
        if score <= SIMILARITY_THRESHOLD
    ]

    if verbose:
        print(f"[RETRIEVER] After similarity threshold ({SIMILARITY_THRESHOLD}): "
              f"{len(threshold_passed)}/{len(filtered_docs)} chunks passed")

    # Soft fallback: if too few pass strict threshold, take the best available
    if len(threshold_passed) < 2 and len(filtered_docs) > 0:
        logging.info(f"SOFT_FALLBACK | query='{query}' | "
                     f"strict_passed={len(threshold_passed)} | using top loosest chunks")
        threshold_passed = filtered_docs[:CONFIDENCE_LOW_FALLBACK_K]

    # STEP 5: Cross-encoder reranking
    if len(threshold_passed) > 0:
        pairs = [(query, doc.page_content) for doc, _ in threshold_passed]
        rerank_scores = RERANKER.predict(pairs)

        ranked = sorted(
            zip([doc for doc, _ in threshold_passed],
                [score for _, score in threshold_passed],
                rerank_scores),
            key=lambda x: x[2],
            reverse=True
        )

        reranked_above_threshold = [
            (doc, l2_score, rscore)
            for doc, l2_score, rscore in ranked
            if rscore >= RERANK_SCORE_THRESHOLD
        ]

        all_reranked = [(doc, l2_score, rscore) for doc, l2_score, rscore in ranked]
    else:
        reranked_above_threshold = []
        all_reranked = []

    if verbose:
        print(f"[RETRIEVER] After rerank threshold ({RERANK_SCORE_THRESHOLD}): "
              f"{len(reranked_above_threshold)}/{len(threshold_passed)} chunks passed")

    # STEP 5b: Determine confidence and select final chunks
    top_rerank_score = float(all_reranked[0][2]) if all_reranked else 0.0

    if (len(reranked_above_threshold) >= CONFIDENCE_HIGH_MIN_CHUNKS
            and top_rerank_score >= CONFIDENCE_HIGH_MIN_SCORE):
        confidence = "high"
        final_chunks = reranked_above_threshold[:TOP_K_RERANK]
    elif (len(reranked_above_threshold) >= CONFIDENCE_MEDIUM_MIN_CHUNKS
            and top_rerank_score >= CONFIDENCE_MEDIUM_MIN_SCORE):
        confidence = "medium"
        final_chunks = reranked_above_threshold[:TOP_K_RERANK]
    else:
        confidence = "low"
        final_chunks = all_reranked[:CONFIDENCE_LOW_FALLBACK_K] if all_reranked else []

    if verbose:
        print(f"[RETRIEVER] Confidence: {confidence.upper()} "
              f"(top_rerank={top_rerank_score:.3f}, chunks={len(final_chunks)})")

    # STEP 6: Assemble context for LLM
    context_blocks = []
    pages_used = []
    sections_used = []
    conditions_used = []

    for rank, (doc, l2_score, rscore) in enumerate(final_chunks, 1):
        meta = doc.metadata
        block = format_context_block(doc.page_content, meta, rank, l2_score, rscore)
        context_blocks.append(block)
        pages_used.append(meta.get("page_number"))
        sections_used.append(meta.get("section_name"))
        conditions_used.append(meta.get("condition"))

    context = "\n---\n".join(context_blocks) if context_blocks else None

    logging.info(
        f"RETRIEVAL | query='{query}' | qtype={qtype} | condition={condition} | "
        f"confidence={confidence} | "
        f"stage1={len(docs_and_scores)} | threshold_passed={len(threshold_passed)} | "
        f"rerank_passed={len(reranked_above_threshold)} | final={len(final_chunks)} | "
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
            "stage1_count": len(docs_and_scores),
            "threshold_passed": len(threshold_passed),
            "rerank_passed": len(reranked_above_threshold),
            "final_count": len(final_chunks),
            "top_rerank_score": top_rerank_score,
        },
        "confidence": confidence,
    }
