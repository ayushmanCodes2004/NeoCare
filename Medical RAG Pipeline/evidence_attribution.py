# ============================================================
# evidence_attribution.py — Evidence Attribution Layer
# ============================================================
"""
Evidence Attribution Layer

Verifies that every recommendation/claim in the LLM output
is explicitly grounded in retrieved chunks.

Prevents hallucinations by:
1. Extracting claims from LLM output
2. Checking if each claim appears in retrieved text
3. Flagging ungrounded claims
4. Removing or marking speculative content
"""

import re
from typing import List, Dict, Tuple


class EvidenceAttributor:
    """
    Verifies evidence grounding for LLM outputs.
    Prevents hallucinations by checking claim-evidence alignment.
    """
    
    # Patterns for extracting recommendations/claims
    RECOMMENDATION_PATTERNS = [
        r'(?:recommend|should|must|require|need)[^.!?]*[.!?]',
        r'(?:delivery|refer|monitor|test|screen)[^.!?]*[.!?]',
        r'(?:\d+\s*(?:week|mg|unit|dose))[^.!?]*[.!?]',
    ]
    
    # High-risk phrases that need strong evidence
    HIGH_RISK_PHRASES = [
        'delivery should be planned',
        'genetic counseling',
        'weekly',
        'daily',
        'immediate',
        'urgent',
        'specialist',
        'tertiary',
        'lft', 'kft', 'rft',  # Lab tests
        'specific weeks',
        'specific dosage',
        'blood transfusion',  # Severity escalation
        'transfusion',
        'fru referral',  # First Referral Unit
        'tertiary center',
    ]
    
    # Severity constraint filters (prevent escalation)
    SEVERITY_CONSTRAINTS = {
        'moderate_anemia': [
            'blood transfusion',
            'transfusion',
            'severe anemia',
            'fru referral',
        ],
        'mild_anemia': [
            'blood transfusion',
            'transfusion',
            'moderate anemia',
            'severe anemia',
            'fru referral',
        ],
        'hypertension': [
            'severe hypertension',
            'eclampsia',
            'immediate delivery',
        ],
    }
    
    def __init__(self, rule_output=None):
        """
        Initialize attributor.
        
        Args:
            rule_output: Optional RuleEngineOutput to check severity constraints
        """
        self.rule_output = rule_output
    
    def verify_grounding(self,
                         llm_output: str,
                         retrieved_chunks: List[Tuple],
                         verbose: bool = False) -> Dict:
        """
        Verify that LLM output is grounded in retrieved evidence.
        
        Args:
            llm_output: Generated text from LLM
            retrieved_chunks: List of (doc, score) tuples
            verbose: Print verification details
            
        Returns:
            Dict with grounding analysis
        """
        if verbose:
            print("\n[EVIDENCE ATTRIBUTION] Verifying grounding...")
        
        # Combine all retrieved text
        all_evidence = " ".join([
            doc.page_content.lower() 
            for doc, _ in retrieved_chunks
        ])
        
        # Extract claims from output
        claims = self._extract_claims(llm_output)
        
        # Check each claim
        grounded_claims = []
        ungrounded_claims = []
        speculative_claims = []
        severity_violations = []  # NEW: Track severity escalations
        
        for claim in claims:
            claim_lower = claim.lower()
            
            # Check for severity constraint violations
            if self.rule_output:
                severity_violation = self._check_severity_constraints(claim_lower)
                if severity_violation:
                    severity_violations.append(claim)
                    ungrounded_claims.append(claim)
                    if verbose:
                        print(f"  ⚠️  SEVERITY VIOLATION: {claim[:80]}... ({severity_violation})")
                    continue
            
            # Check if claim contains high-risk phrases
            is_high_risk = any(
                phrase in claim_lower 
                for phrase in self.HIGH_RISK_PHRASES
            )
            
            # Check if claim is in evidence
            is_grounded = self._check_grounding(claim_lower, all_evidence)
            
            if is_grounded:
                grounded_claims.append(claim)
            elif is_high_risk:
                ungrounded_claims.append(claim)
                if verbose:
                    print(f"  ⚠️  UNGROUNDED HIGH-RISK: {claim[:80]}...")
            else:
                speculative_claims.append(claim)
                if verbose:
                    print(f"  ⚠️  SPECULATIVE: {claim[:80]}...")
        
        # Calculate grounding score
        total_claims = len(claims)
        if total_claims > 0:
            grounding_score = len(grounded_claims) / total_claims
        else:
            grounding_score = 1.0  # No claims = fully grounded
        
        result = {
            'grounding_score': grounding_score,
            'total_claims': total_claims,
            'grounded_claims': len(grounded_claims),
            'ungrounded_claims': len(ungrounded_claims),
            'speculative_claims': len(speculative_claims),
            'ungrounded_list': ungrounded_claims,
            'speculative_list': speculative_claims,
            'is_safe': len(ungrounded_claims) == 0,  # Safe if no ungrounded high-risk claims
        }
        
        if verbose:
            print(f"[EVIDENCE ATTRIBUTION] Grounding Score: {grounding_score:.2f}")
            print(f"[EVIDENCE ATTRIBUTION] Grounded: {len(grounded_claims)}/{total_claims}")
            print(f"[EVIDENCE ATTRIBUTION] Ungrounded High-Risk: {len(ungrounded_claims)}")
            print(f"[EVIDENCE ATTRIBUTION] Speculative: {len(speculative_claims)}")
        
        return result
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract claims/recommendations from text."""
        claims = []
        
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains recommendation patterns
            for pattern in self.RECOMMENDATION_PATTERNS:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence)
                    break
            
            # Also check for high-risk phrases
            for phrase in self.HIGH_RISK_PHRASES:
                if phrase in sentence.lower():
                    claims.append(sentence)
                    break
        
        return list(set(claims))  # Deduplicate
    
    def _check_severity_constraints(self, claim: str) -> str:
        """
        Check if claim violates severity constraints.
        
        Returns violation type if found, None otherwise.
        """
        if not self.rule_output:
            return None
        
        # Check what severity levels are present in rule output
        triggered_rules = self.rule_output.triggered_rules
        
        # Moderate anemia: forbid transfusion/severe anemia mentions
        if 'moderate_anemia' in triggered_rules:
            for forbidden in self.SEVERITY_CONSTRAINTS['moderate_anemia']:
                if forbidden in claim:
                    return f"moderate anemia cannot have '{forbidden}'"
        
        # Mild anemia: forbid transfusion/moderate/severe mentions
        if 'mild_anemia' in triggered_rules:
            for forbidden in self.SEVERITY_CONSTRAINTS['mild_anemia']:
                if forbidden in claim:
                    return f"mild anemia cannot have '{forbidden}'"
        
        # Hypertension (not severe): forbid severe hypertension mentions
        if 'hypertension' in triggered_rules and 'severe_hypertension' not in triggered_rules:
            for forbidden in self.SEVERITY_CONSTRAINTS['hypertension']:
                if forbidden in claim:
                    return f"hypertension (not severe) cannot have '{forbidden}'"
        
        return None
    
    def _check_grounding(self, claim: str, evidence: str) -> bool:
        """
        Check if claim is grounded in evidence.
        
        Uses fuzzy matching to allow for paraphrasing.
        """
        # Extract key terms from claim (nouns, numbers, medical terms)
        key_terms = self._extract_key_terms(claim)
        
        if not key_terms:
            return True  # No specific terms to check
        
        # Check if majority of key terms appear in evidence
        found_terms = sum(1 for term in key_terms if term in evidence)
        
        # Require at least 70% of key terms to be present
        threshold = 0.7
        return (found_terms / len(key_terms)) >= threshold
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key medical/clinical terms from text."""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'it', 'its'
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter
        key_terms = [
            word for word in words 
            if word not in stop_words and len(word) > 3
        ]
        
        return key_terms
    
    def clean_output(self,
                     llm_output: str,
                     grounding_result: Dict) -> str:
        """
        Clean LLM output by removing/marking ungrounded claims.
        
        Args:
            llm_output: Original LLM output
            grounding_result: Result from verify_grounding
            
        Returns:
            Cleaned output with ungrounded claims removed/marked
        """
        if grounding_result['is_safe']:
            return llm_output  # No changes needed
        
        cleaned = llm_output
        
        # Remove ungrounded high-risk claims
        for claim in grounding_result['ungrounded_list']:
            # Remove the claim
            cleaned = cleaned.replace(claim, '')
        
        # Mark speculative claims
        for claim in grounding_result['speculative_list']:
            # Add disclaimer
            marked = f"{claim} [General clinical practice - verify with guidelines]"
            cleaned = cleaned.replace(claim, marked)
        
        # Add warning if claims were removed
        if grounding_result['ungrounded_claims'] > 0:
            warning = f"\n\n⚠️ Note: {grounding_result['ungrounded_claims']} ungrounded recommendations were removed for safety."
            cleaned += warning
        
        return cleaned
