# ============================================================
# rag_pipeline.py — Full RAG chain with confidence-based responses
# ============================================================

import re
import logging
import requests
from config import *
from retriever import retrieve

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

# ============================================================
# SYSTEM PROMPTS — one per confidence tier
# ============================================================

SYSTEM_PROMPT_HIGH = """You are a specialized medical AI assistant for maternal and reproductive health in India.
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

SYSTEM_PROMPT_MEDIUM = """You are a specialized medical AI assistant for maternal and reproductive health in India.
You answer questions based on the provided context extracted from a merged document containing:
a research paper on high-risk pregnancy prevalence (NFHS-5 data), clinical management guidelines
for HRP conditions (hypertension, anaemia, GDM, hypothyroidism, syphilis, IUGR, previous CS,
placenta previa, twins), Government of India health schemes (PMSMA, JSY, JSSK, PMMMVY, DAKSHATA),
and clinical procedure reference charts (ANC, PPH, AMTSL, eclampsia, neonatal resuscitation).

IMPORTANT RULES:
- The retrieved context may be only partially relevant to the question.
- Answer based on what IS available in the context, clearly stating what information comes from the document.
- Use cautious language like "Based on the available context...", "The document indicates that...",
  "According to the retrieved sections..." to signal partial grounding.
- If only part of the question can be answered from context, answer that part and explicitly note
  what aspects are not covered in the retrieved sections.
- Do NOT fabricate information. Only state what the context supports.
- For drug dosages and statistics, reproduce EXACT values from context.
- If a question involves emergency clinical management, append:
  "[CLINICAL DECISION — VERIFY WITH QUALIFIED TREATING PHYSICIAN BEFORE ACTING]"
- If the question is about drug dosage, append:
  "[DOSAGE — CONFIRM WITH PRESCRIBING PHYSICIAN. THIS IS DOCUMENT REFERENCE ONLY]"
"""

SYSTEM_PROMPT_LOW = """You are a specialized medical AI assistant for maternal and reproductive health in India.
You are working with a document that covers:
- High-risk pregnancy prevalence in India (NFHS-5 data, Kuppusamy et al., 2023)
- Clinical guidelines for: hypertension/eclampsia, anaemia, GDM, hypothyroidism, syphilis,
  IUGR, previous caesarean, placenta previa, twin pregnancy
- Government health schemes: PMSMA, JSY, JSSK, PMMMVY, DAKSHATA
- Clinical procedure charts: ANC, postnatal care, PPH, AMTSL, eclampsia, neonatal resuscitation
- PMSMA monitoring checklists

IMPORTANT RULES:
- The retrieved context has LOW relevance to the user's question.
- DO NOT make up an answer. Instead, provide a helpful soft-grounded response:
  1. Briefly state what the document primarily covers (the topics above).
  2. If the retrieved context contains ANY tangentially related information, mention it with
     clear hedging: "While not directly addressing your question, the document does discuss..."
  3. Suggest which specific topics from the document might be relevant to explore.
- NEVER fabricate statistics, drug dosages, or clinical protocols.
- Keep the response honest about the limitations while being maximally helpful.
- If a question involves emergency clinical management, append:
  "[CLINICAL DECISION — VERIFY WITH QUALIFIED TREATING PHYSICIAN BEFORE ACTING]"
"""

# ============================================================
# QUERY PROMPT TEMPLATES — one per confidence tier
# ============================================================

QUERY_PROMPT_HIGH = """Context retrieved from the medical document (HIGH relevance):

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

QUERY_PROMPT_MEDIUM = """Context retrieved from the medical document (PARTIAL relevance — some sections may be tangential):

{context}

---

Question: {question}

Instructions for answering:
- Answer based on what IS available in the context above.
- Use cautious language: "Based on the available context...", "The document indicates..."
- If only part of the question is answerable from context, answer that part clearly.
- Explicitly note which aspects of the question are NOT covered in the retrieved context.
- Do NOT fabricate or extrapolate. Only state what the context directly supports.
- For any statistics or drug dosages, use EXACT values from the context.
- At the end of your answer, on a new line, write: "Source: Page(s) [list page numbers] — [list section names]"
- On the next line write: "Note: This answer is based on partially relevant context. Some aspects may not be fully covered."

Answer:"""

QUERY_PROMPT_LOW = """Context retrieved from the medical document (LOW relevance — these are the closest available sections):

{context}

---

Question: {question}

Instructions for answering:
- The retrieved context has low relevance to this specific question.
- DO NOT fabricate an answer. Instead, provide a helpful response:
  1. Start by acknowledging that the document does not directly address this specific question.
  2. Mention what the document DOES cover that might be related (use the context above for clues).
  3. If the context contains ANY tangentially related information, share it with clear hedging:
     "While not directly addressing your question, the document does discuss..."
  4. Suggest specific topics from the document the user could ask about instead.
- NEVER make up statistics, drug dosages, or clinical protocols.
- Be honest but maximally helpful.

Answer:"""

QUERY_PROMPT_NO_CONTEXT = """Question: {question}

The retrieval system could not find any relevant sections in the medical document for this question.

The document primarily covers:
- High-risk pregnancy prevalence in India (NFHS-5 data, 23,853 pregnant women)
- Clinical management guidelines for: hypertension/eclampsia, anaemia, GDM, hypothyroidism,
  syphilis, IUGR, previous caesarean section, placenta previa, twin pregnancy
- Government of India health schemes: PMSMA, JSY, JSSK, PMMMVY, DAKSHATA
- Clinical procedure charts: ANC checkup, postnatal care, PPH management, AMTSL,
  eclampsia management, neonatal resuscitation, breastfeeding, infection prevention
- PMSMA onsite monitoring and self-assessment checklists

Instructions:
- Acknowledge that this specific question is not covered in the document.
- Mention which of the above topics might be most relevant or related to the user's question.
- Suggest 2-3 specific questions the user could ask that ARE covered by the document.
- Do NOT fabricate any medical information.

Answer:"""


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


def get_prompt_for_confidence(confidence: str, context: str | None, question: str) -> tuple[str, str]:
    """
    Select system prompt and query template based on confidence tier.
    Returns (system_prompt, user_prompt) tuple.
    """
    if context is None or confidence == "low":
        if context:
            system_prompt = SYSTEM_PROMPT_LOW
            user_prompt = QUERY_PROMPT_LOW.format(context=context, question=question)
        else:
            system_prompt = SYSTEM_PROMPT_LOW
            user_prompt = QUERY_PROMPT_NO_CONTEXT.format(question=question)
    elif confidence == "medium":
        system_prompt = SYSTEM_PROMPT_MEDIUM
        user_prompt = QUERY_PROMPT_MEDIUM.format(context=context, question=question)
    else:
        system_prompt = SYSTEM_PROMPT_HIGH
        user_prompt = QUERY_PROMPT_HIGH.format(context=context, question=question)

    return system_prompt, user_prompt


def validate_answer(answer: str, retrieved_chunks: list, confidence: str = "high") -> dict:
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

    no_answer_signals = [
        "not available in the provided document",
        "not found in the context",
        "cannot find this information",
        "not mentioned in the document",
        "does not directly address",
        "not directly covered",
    ]
    if any(signal in answer.lower() for signal in no_answer_signals):
        validation["is_no_answer"] = True

    if confidence != "low":
        numbers_in_answer = re.findall(r'\b\d+\.?\d*%?\b', answer)
        all_chunk_text = ""
        if retrieved_chunks:
            for c in retrieved_chunks:
                if hasattr(c[0], "page_content"):
                    all_chunk_text += " " + c[0].page_content
                else:
                    all_chunk_text += " " + str(c[0])

        hallucinated = []
        for num in numbers_in_answer:
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

    if len(answer.strip()) < 50:
        validation["is_incomplete"] = True
        validation["warnings"].append(
            "WARNING: Answer appears very short. Response may be incomplete."
        )

    return validation


def run_rag(query: str, verbose: bool = True) -> dict:
    """
    Full RAG pipeline with confidence-based responses:
    1. Retrieve relevant chunks (with confidence scoring)
    2. Select prompt template based on confidence tier
    3. Call LLM with appropriate system prompt
    4. Validate answer
    5. Return full result dict with confidence metadata
    """
    # STEP 1: Retrieval with confidence scoring
    retrieval_result = retrieve(query, verbose=verbose)
    confidence = retrieval_result.get("confidence", "low")
    context = retrieval_result.get("context")

    if verbose:
        print(f"[RAG] Confidence tier: {confidence.upper()}")

    # STEP 2: Select prompt based on confidence
    system_prompt, user_prompt = get_prompt_for_confidence(confidence, context, query)

    # STEP 3: Call LLM
    if verbose:
        print(f"[RAG] Calling {OLLAMA_MODEL} with temperature={TEMPERATURE}...")

    answer = call_ollama(system_prompt, user_prompt)

    # STEP 4: Validate answer
    validation = validate_answer(answer, retrieval_result.get("chunks", []), confidence)

    if validation["warnings"]:
        answer += "\n\n" + "\n".join(validation["warnings"])

    # STEP 5: Add confidence badge to answer
    confidence_badges = {
        "high": "\n\n[✅ HIGH CONFIDENCE — Fully grounded in document]",
        "medium": "\n\n[⚠️ MEDIUM CONFIDENCE — Partially grounded. Verify with original document.]",
        "low": "\n\n[ℹ️ LOW CONFIDENCE — Limited document coverage. Treat as guidance only.]",
    }
    answer += confidence_badges.get(confidence, "")

    logging.info(
        f"RAG_COMPLETE | query='{query}' | confidence={confidence} | "
        f"pages={retrieval_result.get('metadata_used', {}).get('pages')} | "
        f"hallucination_flag={validation['hallucination_flag']} | "
        f"answer_length={len(answer)}"
    )

    return {
        "query": query,
        "answer": answer,
        "confidence": confidence,
        "metadata_used": retrieval_result.get("metadata_used", {}),
        "retrieval_stats": retrieval_result.get("retrieval_stats", {}),
        "validation": validation,
    }
