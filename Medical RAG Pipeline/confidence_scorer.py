# ============================================================
# confidence_scorer.py — Weighted Confidence Scoring
# ============================================================
"""
Confidence Scoring System

Formula:
confidence = 0.4 * retrieval_quality + 
             0.3 * rule_coverage + 
             0.2 * chunk_agreement + 
             0.1 * extractor_confidence
"""

from typing import Dict
from config_production import CONFIDENCE_WEIGHTS, CONFIDENCE_THRESHOLDS


def calculate_confidence(
    retrieval_quality: float,
    rule_coverage: float,
    chunk_agreement: float,
    extractor_confidence: float,
    input_type: str = "text",  # FIX 2: Add input_type parameter
    verbose: bool = False
) -> Dict:
    """
    Calculate weighted confidence score with safety ceilings.
    
    CRITICAL SAFETY RULES:
    1. If retrieval_quality < 0.4: Cap confidence at 0.6 (MEDIUM max)
    2. If rule_coverage < 0.5: Reduce confidence by 15%
    3. If input_type == "structured_json": Min confidence 0.70
    
    Args:
        retrieval_quality: Avg top-3 similarity (0-1)
        rule_coverage: % features with rules (0-1)
        chunk_agreement: Multi-chunk support (0-1)
        extractor_confidence: Feature extraction quality (0-1)
        input_type: "text" or "structured_json"
        verbose: Print breakdown
        
    Returns:
        Dict with score, level, and breakdown
    """
    # Calculate weighted score
    score = (
        CONFIDENCE_WEIGHTS['retrieval_quality'] * retrieval_quality +
        CONFIDENCE_WEIGHTS['rule_coverage'] * rule_coverage +
        CONFIDENCE_WEIGHTS['chunk_agreement'] * chunk_agreement +
        CONFIDENCE_WEIGHTS['extractor_confidence'] * extractor_confidence
    )
    
    # CRITICAL: Apply confidence ceilings for safety
    original_score = score
    ceiling_applied = []
    
    # Ceiling 1: Weak retrieval = max MEDIUM confidence
    if retrieval_quality < 0.4:
        score = min(score, 0.6)
        ceiling_applied.append(f"weak_retrieval (quality={retrieval_quality:.2f})")
    
    # Ceiling 2: Low rule coverage = reduce confidence
    if rule_coverage < 0.5:
        score *= 0.85
        ceiling_applied.append(f"low_rule_coverage (coverage={rule_coverage:.2f})")
    
    # Ceiling 3: Very weak retrieval = max LOW confidence
    if retrieval_quality < 0.25:
        score = min(score, 0.45)
        ceiling_applied.append(f"very_weak_retrieval (quality={retrieval_quality:.2f})")
    
    # FIX 2: Structured JSON input gets minimum 0.70 confidence
    if input_type == "structured_json":
        score = max(0.70, score)
        if score == 0.70 and original_score < 0.70:
            ceiling_applied.append("structured_json_minimum (min=0.70)")
    
    # Determine confidence level (STRICT MAPPING)
    if score >= CONFIDENCE_THRESHOLDS['high']:
        level = 'HIGH'
    elif score >= CONFIDENCE_THRESHOLDS['medium']:
        level = 'MEDIUM'
    elif score >= CONFIDENCE_THRESHOLDS['low']:
        level = 'LOW'
    else:
        level = 'VERY_LOW'
    
    result = {
        'score': score,
        'level': level,
        'original_score': original_score,
        'ceiling_applied': ceiling_applied,
        'breakdown': {
            'retrieval_quality': retrieval_quality,
            'rule_coverage': rule_coverage,
            'chunk_agreement': chunk_agreement,
            'extractor_confidence': extractor_confidence,
        },
        'weights': CONFIDENCE_WEIGHTS,
    }
    
    if verbose:
        print(f"\n[CONFIDENCE] Overall Score: {score:.2f} ({level})")
        if ceiling_applied:
            print(f"[CONFIDENCE] ⚠️  Confidence ceiling applied: {', '.join(ceiling_applied)}")
            print(f"[CONFIDENCE] Original score: {original_score:.2f} → Capped: {score:.2f}")
        print(f"[CONFIDENCE] Breakdown:")
        print(f"  - Retrieval Quality: {retrieval_quality:.2f} (weight: {CONFIDENCE_WEIGHTS['retrieval_quality']})")
        print(f"  - Rule Coverage: {rule_coverage:.2f} (weight: {CONFIDENCE_WEIGHTS['rule_coverage']})")
        print(f"  - Chunk Agreement: {chunk_agreement:.2f} (weight: {CONFIDENCE_WEIGHTS['chunk_agreement']})")
        print(f"  - Extractor Confidence: {extractor_confidence:.2f} (weight: {CONFIDENCE_WEIGHTS['extractor_confidence']})")
    
    return result
