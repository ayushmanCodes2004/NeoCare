# ============================================================
# hallucination_guard.py — Hallucination Prevention Guards
# ============================================================
"""
Hallucination Guard System

Blocks output if:
- confidence_score < 0.35 OR
- retrieval_quality < 0.35

Returns: "LOW CONFIDENCE — INSUFFICIENT DOCUMENT EVIDENCE"
"""

from typing import Dict
from config_production import HALLUCINATION_GUARD_THRESHOLD


def check_hallucination_risk(
    confidence_score: float,
    retrieval_quality: float,
    verbose: bool = False
) -> Dict:
    """
    Check if output should be blocked due to hallucination risk.
    
    Args:
        confidence_score: Overall confidence (0-1)
        retrieval_quality: Retrieval quality (0-1)
        verbose: Print guard status
        
    Returns:
        Dict with allow_output, reason, recommendations_disabled
    """
    # Check thresholds
    confidence_too_low = confidence_score < HALLUCINATION_GUARD_THRESHOLD
    retrieval_too_low = retrieval_quality < HALLUCINATION_GUARD_THRESHOLD
    
    if confidence_too_low or retrieval_too_low:
        reasons = []
        if confidence_too_low:
            reasons.append(f"Overall confidence ({confidence_score:.2f}) below threshold ({HALLUCINATION_GUARD_THRESHOLD})")
        if retrieval_too_low:
            reasons.append(f"Retrieval quality ({retrieval_quality:.2f}) below threshold ({HALLUCINATION_GUARD_THRESHOLD})")
        
        result = {
            'allow_output': False,
            'reason': 'LOW CONFIDENCE — INSUFFICIENT DOCUMENT EVIDENCE',
            'detailed_reasons': reasons,
            'recommendations_disabled': True,
            'confidence_score': confidence_score,
            'retrieval_quality': retrieval_quality,
        }
        
        if verbose:
            print(f"\n[HALLUCINATION GUARD] ⚠️ OUTPUT BLOCKED")
            print(f"[HALLUCINATION GUARD] Reasons:")
            for reason in reasons:
                print(f"  - {reason}")
        
        return result
    
    # Safe to proceed
    result = {
        'allow_output': True,
        'reason': None,
        'detailed_reasons': [],
        'recommendations_disabled': False,
        'confidence_score': confidence_score,
        'retrieval_quality': retrieval_quality,
    }
    
    if verbose:
        print(f"\n[HALLUCINATION GUARD] ✓ Output allowed (confidence: {confidence_score:.2f}, retrieval: {retrieval_quality:.2f})")
    
    return result


def format_blocked_response(guard_result: Dict) -> str:
    """
    Format response when output is blocked.
    
    Args:
        guard_result: Result from check_hallucination_risk
        
    Returns:
        Formatted blocked response
    """
    response = f"""[CLINICAL DECISION SUPPORT — NOT A DIAGNOSIS]

⚠️ {guard_result['reason']}

The system cannot provide a reliable answer for this query due to:
"""
    
    for reason in guard_result['detailed_reasons']:
        response += f"\n  • {reason}"
    
    response += """

This may occur when:
- The query is outside the scope of the clinical document
- Insufficient relevant information was retrieved
- The extracted clinical features are incomplete

Please:
1. Rephrase your query with more specific clinical details
2. Ensure the query relates to high-risk pregnancy topics covered in the document
3. Consult a qualified healthcare professional for clinical guidance

Document Coverage:
- High-risk pregnancy prevalence in India (NFHS-5 data)
- Clinical management: hypertension, anaemia, GDM, hypothyroidism, IUGR, twins, previous cesarean
- Government schemes: PMSMA, JSY, JSSK, PMMMVY
- Clinical procedures: ANC, PPH, eclampsia management, neonatal resuscitation

[Consult qualified physician for all clinical decisions]
"""
    
    return response
