# ============================================================
# controlled_generator.py — Controlled LLM generation with clinical prompts
# ============================================================
"""
LAYER 4: Controlled Generation
- Clinical-aware prompts
- Confidence-based response strategies
- Grounded reasoning
- Citation requirements
- Smart fallback logic
"""

import requests
from typing import Dict, Optional
from config import OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS, TOP_P
from clinical_risk_scorer import RiskAssessment


class ControlledGenerator:
    """
    LLM generation with clinical safety controls.
    Adapts prompts based on confidence and risk assessment.
    """
    
    # System prompts for different confidence levels
    SYSTEM_PROMPT_HIGH = """You are a specialized medical AI assistant for high-risk pregnancy detection.
You answer questions STRICTLY based on the provided clinical context.

CRITICAL RULES:
1. Base ALL answers on the provided context chunks
2. For clinical decisions, cite specific page numbers and sections
3. Use clear yes/no answers for high-risk pregnancy classification
4. Provide bullet-point reasoning with evidence
5. NEVER fabricate statistics, drug dosages, or clinical protocols
6. If context contains conflicting information, acknowledge it
7. For emergency conditions, add appropriate clinical warnings

RESPONSE FORMAT:
- Start with clear HIGH-RISK or NOT HIGH-RISK classification (if applicable)
- List risk factors with evidence from context
- Cite page numbers for all clinical claims
- End with clinical recommendations if appropriate

This is HIGH CONFIDENCE retrieval - the context is highly relevant."""

    SYSTEM_PROMPT_MEDIUM = """You are a specialized medical AI assistant for high-risk pregnancy detection.
You answer questions based on the provided clinical context, which may be partially relevant.

IMPORTANT RULES:
1. Answer based on what IS available in the context
2. Use cautious language: "Based on available context...", "The document indicates..."
3. Clearly state what aspects are NOT covered in the retrieved sections
4. Do NOT fabricate information to fill gaps
5. Cite page numbers for all claims
6. If only partial information is available, acknowledge limitations

RESPONSE FORMAT:
- Provide grounded answer based on available context
- Explicitly note information gaps
- Use hedging language appropriately
- Cite sources for all claims

This is MEDIUM CONFIDENCE retrieval - context may be incomplete."""

    SYSTEM_PROMPT_LOW = """You are a specialized medical AI assistant for high-risk pregnancy detection.
The retrieved context has LOW relevance to the user's question.

CRITICAL RULES:
1. DO NOT fabricate an answer
2. Acknowledge that the document does not directly address this question
3. If context contains ANY tangentially related information, share it with clear hedging
4. Suggest what topics the document DOES cover that might be relevant
5. NEVER make up statistics, dosages, or clinical protocols

RESPONSE FORMAT:
- Acknowledge limited document coverage
- Share any tangentially related information from context (if any)
- Suggest related topics the user could ask about
- Be honest about limitations

This is LOW CONFIDENCE retrieval - context is not well-matched to query."""

    def __init__(self):
        """Initialize generator."""
        pass
    
    def generate(self,
                 query: str,
                 context: Optional[str],
                 confidence: str,
                 risk_assessment: Optional[RiskAssessment] = None,
                 verbose: bool = True) -> Dict:
        """
        Generate controlled response with clinical awareness.
        
        Args:
            query: Original user query
            context: Retrieved context (or None)
            confidence: Confidence level ("high", "medium", "low")
            risk_assessment: Clinical risk assessment (if available)
            verbose: Print debug info
            
        Returns:
            Dict with answer, confidence, and metadata
        """
        if verbose:
            print(f"\n[GENERATOR] Generating response with {confidence.upper()} confidence")
        
        # Select system prompt based on confidence
        if confidence == "high":
            system_prompt = self.SYSTEM_PROMPT_HIGH
        elif confidence == "medium":
            system_prompt = self.SYSTEM_PROMPT_MEDIUM
        else:
            system_prompt = self.SYSTEM_PROMPT_LOW
        
        # Build user prompt
        user_prompt = self._build_user_prompt(query, context, confidence, risk_assessment)
        
        # Call LLM
        answer = self._call_openai(system_prompt, user_prompt)
        
        # Post-process answer
        answer = self._post_process_answer(answer, confidence, risk_assessment)
        
        return {
            'answer': answer,
            'confidence': confidence,
            'system_prompt_used': confidence,
        }
    
    def _build_user_prompt(self,
                           query: str,
                           context: Optional[str],
                           confidence: str,
                           risk_assessment: Optional[RiskAssessment]) -> str:
        """Build user prompt with context and risk assessment."""
        parts = []
        
        # Add risk assessment if available
        if risk_assessment:
            parts.append("=== CLINICAL RISK ASSESSMENT ===")
            parts.append(f"Risk Level: {risk_assessment.risk_level.upper()}")
            parts.append(f"Risk Score: {risk_assessment.total_score}")
            
            if risk_assessment.risk_factors:
                parts.append("\nIdentified Risk Factors:")
                for rf in risk_assessment.risk_factors:
                    parts.append(f"  • {rf['factor']}: {rf['value']} (Severity: {rf['severity']})")
            
            parts.append("\n")
        
        # Add retrieved context
        if context:
            parts.append("=== RETRIEVED CLINICAL CONTEXT ===")
            parts.append(context)
            parts.append("\n")
        else:
            parts.append("=== NO RELEVANT CONTEXT RETRIEVED ===")
            parts.append("The retrieval system could not find relevant sections for this query.")
            parts.append("\n")
        
        # Add query
        parts.append("=== USER QUESTION ===")
        parts.append(query)
        parts.append("\n")
        
        # Add instructions based on confidence
        parts.append("=== INSTRUCTIONS ===")
        if confidence == "high":
            parts.append("Provide a comprehensive, evidence-based answer using the context above.")
            parts.append("Format: Clear classification → Risk factors with evidence → Recommendations")
            parts.append("Cite page numbers for all clinical claims.")
        elif confidence == "medium":
            parts.append("Provide a grounded answer based on available context.")
            parts.append("Clearly state what information is available and what is missing.")
            parts.append("Use cautious language and cite sources.")
        else:
            parts.append("Acknowledge that the document does not directly address this question.")
            parts.append("Share any tangentially related information if available.")
            parts.append("Suggest related topics the user could ask about.")
        
        parts.append("\nYour response:")
        
        return "\n".join(parts)
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API with controlled parameters."""
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": TEMPERATURE,  # 0.0 for deterministic
            "max_tokens": MAX_TOKENS,
            "top_p": TOP_P,
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Cannot connect to OpenAI API. Check your internet connection."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("OpenAI API request timed out after 120 seconds.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid OpenAI API key. Please check your API key.")
            elif e.response.status_code == 429:
                raise ValueError("OpenAI API rate limit exceeded. Please try again later.")
            else:
                raise ValueError(f"OpenAI API error: {e.response.text}")
    
    def _post_process_answer(self,
                             answer: str,
                             confidence: str,
                             risk_assessment: Optional[RiskAssessment]) -> str:
        """Post-process answer with confidence badges and warnings."""
        # Add confidence badge
        confidence_badges = {
            "high": "\n\n✅ [HIGH CONFIDENCE — Fully grounded in clinical document]",
            "medium": "\n\n⚠️ [MEDIUM CONFIDENCE — Partially grounded. Verify with original document.]",
            "low": "\n\n ℹ️ [LOW CONFIDENCE — Limited document coverage. Treat as guidance only.]",
        }
        answer += confidence_badges.get(confidence, "")
        
        # Add clinical warning if high-risk detected
        if risk_assessment and risk_assessment.risk_level in ["high", "critical"]:
            answer += "\n\n⚠️ [CLINICAL WARNING: HIGH-RISK PREGNANCY DETECTED — Specialist consultation required]"
        
        # Add emergency disclaimer if relevant keywords present
        emergency_keywords = ['eclampsia', 'seizure', 'severe bleeding', 'hemorrhage', 
                              'emergency', 'urgent', 'critical']
        if any(kw in answer.lower() for kw in emergency_keywords):
            answer += "\n\n🚨 [EMERGENCY CLINICAL DECISION — VERIFY WITH QUALIFIED PHYSICIAN BEFORE ACTING]"
        
        return answer
    
    def generate_no_context_response(self, query: str) -> str:
        """Generate response when no context is retrieved."""
        return f"""I could not find relevant information in the clinical document to answer your question: "{query}"

The document primarily covers:
- High-risk pregnancy prevalence in India (NFHS-5 data)
- Clinical management guidelines for: hypertension/eclampsia, anaemia, GDM, hypothyroidism, syphilis, IUGR, previous caesarean, placenta previa, twin pregnancy
- Government health schemes: PMSMA, JSY, JSSK, PMMMVY, DAKSHATA
- Clinical procedure charts: ANC, postnatal care, PPH, AMTSL, eclampsia management, neonatal resuscitation

You might want to ask about:
- Prevalence of high-risk pregnancy in India
- Management of specific conditions (hypertension, anemia, diabetes in pregnancy)
- Government maternal health schemes
- Clinical procedures for pregnancy complications

ℹ️ [NO RELEVANT CONTEXT — Question not covered in document]"""
