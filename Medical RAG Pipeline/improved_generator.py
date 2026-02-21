# ============================================================
# improved_generator.py — Coverage-aware generation with clinical rules
# ============================================================
"""
IMPROVED GENERATION:
1. Coverage-aware prompts (derivable vs not available)
2. Clinical rule engine integration
3. No generic fallbacks
4. Document-grounded language
5. Confidence breakdown display
"""

import requests
from typing import Dict, Optional
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, TEMPERATURE, MAX_TOKENS
from clinical_risk_scorer import RiskAssessment
from clinical_preprocessor import ClinicalFeatures


class ImprovedGenerator:
    """
    Coverage-aware LLM generation with clinical rule integration.
    """
    
    # System prompt for derivable knowledge (has rules/thresholds)
    SYSTEM_PROMPT_DERIVABLE = """You are a specialized medical AI assistant for high-risk pregnancy detection.

The retrieved context contains CLINICAL RULES and THRESHOLDS that can be applied to the patient's case.

CRITICAL INSTRUCTIONS:
1. Use the document thresholds to classify the patient's values
2. Apply rules explicitly: "According to document threshold Hb ≥11 g/dL → Normal haemoglobin"
3. Provide clear risk classification based on document criteria
4. Cite specific thresholds and page numbers
5. Use document-grounded language: "Based on document thresholds..." NOT "I think..."
6. NEVER say "not in document" if rules exist - DERIVE the answer from rules
7. Be definitive when rules clearly apply

RESPONSE FORMAT:
1. Clinical Assessment (apply document thresholds to patient values)
2. Risk Classification (based on document criteria)
3. Recommendations (from document guidelines)
4. Source Citations (page numbers)

This is DERIVABLE knowledge - the document provides rules to answer this question."""

    SYSTEM_PROMPT_DIRECT = """You are a specialized medical AI assistant for high-risk pregnancy detection.

The retrieved context DIRECTLY addresses the user's question with specific information.

CRITICAL INSTRUCTIONS:
1. Answer directly from the provided context
2. Cite specific page numbers and sections
3. Use exact statistics, dosages, and protocols from context
4. Provide comprehensive answer based on available information
5. Use document-grounded language
6. Be confident - the context is highly relevant

RESPONSE FORMAT:
- Direct answer to the question
- Supporting evidence from context
- Relevant statistics or protocols
- Source citations

This is DIRECT MATCH - answer confidently from context."""

    SYSTEM_PROMPT_PARTIAL = """You are a specialized medical AI assistant for high-risk pregnancy detection.

The retrieved context provides PARTIAL information related to the question.

CRITICAL INSTRUCTIONS:
1. Answer what IS covered in the context
2. Clearly state what aspects are NOT covered
3. Use cautious language: "The document provides information on X but not Y"
4. Cite sources for all claims
5. Do NOT fabricate missing information
6. Suggest related topics that ARE covered

RESPONSE FORMAT:
- What the document DOES cover (with citations)
- What the document DOES NOT cover (be explicit)
- Related information that may be helpful
- Suggestions for additional questions

This is PARTIAL coverage - be honest about limitations."""

    SYSTEM_PROMPT_NO_COVERAGE = """You are a specialized medical AI assistant for high-risk pregnancy detection.

The retrieved context does NOT cover the user's specific question.

CRITICAL INSTRUCTIONS:
1. Acknowledge that this specific question is not addressed in the document
2. Mention what the document DOES cover that might be related
3. Do NOT fabricate information
4. Suggest specific questions that ARE covered in the document
5. Be helpful but honest about limitations

RESPONSE FORMAT:
- Acknowledge the question is not covered
- Mention related topics that ARE in the document
- Suggest 2-3 specific questions the user could ask instead

This is NO COVERAGE - be honest and helpful."""

    def __init__(self):
        """Initialize generator."""
        pass
    
    def _build_clinical_rule_summary(self, features: ClinicalFeatures) -> str:
        """
        Build clinical rule summary for prompt injection.
        
        Args:
            features: Extracted clinical features
            
        Returns:
            Formatted rule summary
        """
        rules = []
        
        rules.append("=== CLINICAL RULES APPLICATION ===")
        
        # Age rules
        if features.age:
            if features.age >= 35:
                rules.append(f"✓ Age {features.age} years → ADVANCED MATERNAL AGE (≥35 threshold)")
                rules.append("  Document rule: Age ≥35 = High-risk factor")
            elif features.age < 18:
                rules.append(f"✓ Age {features.age} years → TEENAGE PREGNANCY (<18 threshold)")
                rules.append("  Document rule: Age <18 = High-risk factor")
            else:
                rules.append(f"✓ Age {features.age} years → NORMAL AGE RANGE (18-34)")
                rules.append("  Document rule: Age 18-34 = Normal risk")
        
        # Hemoglobin rules
        if features.hemoglobin:
            if features.hemoglobin < 7.0:
                rules.append(f"✓ Hb {features.hemoglobin} g/dL → SEVERE ANAEMIA (<7 threshold)")
                rules.append("  Document rule: Hb <7 = Severe anaemia, urgent treatment")
            elif features.hemoglobin < 10.0:
                rules.append(f"✓ Hb {features.hemoglobin} g/dL → MODERATE ANAEMIA (7-10 threshold)")
                rules.append("  Document rule: Hb 7-10 = Moderate anaemia, requires treatment")
            elif features.hemoglobin < 11.0:
                rules.append(f"✓ Hb {features.hemoglobin} g/dL → MILD ANAEMIA (10-11 threshold)")
                rules.append("  Document rule: Hb 10-11 = Mild anaemia, iron supplementation")
            else:
                rules.append(f"✓ Hb {features.hemoglobin} g/dL → NORMAL HAEMOGLOBIN (≥11 threshold)")
                rules.append("  Document rule: Hb ≥11 = Normal, no anaemia")
        
        # Blood pressure rules
        if features.systolic_bp and features.diastolic_bp:
            if features.systolic_bp >= 160 or features.diastolic_bp >= 110:
                rules.append(f"✓ BP {features.systolic_bp}/{features.diastolic_bp} mmHg → SEVERE HYPERTENSION (≥160/110)")
                rules.append("  Document rule: BP ≥160/110 = Severe, risk of eclampsia")
            elif features.systolic_bp >= 140 or features.diastolic_bp >= 90:
                rules.append(f"✓ BP {features.systolic_bp}/{features.diastolic_bp} mmHg → HYPERTENSION (≥140/90)")
                rules.append("  Document rule: BP ≥140/90 = Hypertension, requires management")
            else:
                rules.append(f"✓ BP {features.systolic_bp}/{features.diastolic_bp} mmHg → NORMAL BLOOD PRESSURE (<140/90)")
                rules.append("  Document rule: BP <140/90 = Normal, no hypertension")
        
        # Glucose rules
        if features.fasting_glucose:
            if features.fasting_glucose >= 126:
                rules.append(f"✓ FBS {features.fasting_glucose} mg/dL → OVERT DIABETES (≥126 threshold)")
                rules.append("  Document rule: FBS ≥126 = Diabetes, requires insulin")
            elif features.fasting_glucose >= 92:
                rules.append(f"✓ FBS {features.fasting_glucose} mg/dL → GESTATIONAL DIABETES (≥92 threshold)")
                rules.append("  Document rule: FBS ≥92 = GDM, requires management")
            else:
                rules.append(f"✓ FBS {features.fasting_glucose} mg/dL → NORMAL GLUCOSE (<92 threshold)")
                rules.append("  Document rule: FBS <92 = Normal, no diabetes")
        
        return "\n".join(rules)
    
    def generate(self,
                 query: str,
                 context: Optional[str],
                 features: ClinicalFeatures,
                 risk_assessment: RiskAssessment,
                 coverage: Dict,
                 confidence_breakdown: Dict,
                 verbose: bool = True) -> Dict:
        """
        Generate coverage-aware response with clinical rules.
        
        Args:
            query: Original query
            context: Retrieved context
            features: Clinical features
            risk_assessment: Risk assessment
            coverage: Coverage analysis
            confidence_breakdown: Confidence score breakdown
            verbose: Print debug info
            
        Returns:
            Generation result dict
        """
        if verbose:
            print(f"\n[GENERATOR] Coverage tier: {coverage['tier']}")
            print(f"[GENERATOR] Derivable: {coverage['derivable']}")
        
        # Select system prompt based on coverage
        if coverage['derivable'] or coverage['tier'] == 'rule_based':
            system_prompt = self.SYSTEM_PROMPT_DERIVABLE
            prompt_type = "derivable"
        elif coverage['tier'] == 'direct_match':
            system_prompt = self.SYSTEM_PROMPT_DIRECT
            prompt_type = "direct"
        elif coverage['has_partial']:
            system_prompt = self.SYSTEM_PROMPT_PARTIAL
            prompt_type = "partial"
        else:
            system_prompt = self.SYSTEM_PROMPT_NO_COVERAGE
            prompt_type = "no_coverage"
        
        if verbose:
            print(f"[GENERATOR] Using prompt type: {prompt_type}")
        
        # Build user prompt
        user_prompt = self._build_user_prompt(
            query, context, features, risk_assessment, coverage, confidence_breakdown
        )
        
        # Call LLM
        answer = self._call_ollama(system_prompt, user_prompt)
        
        # Post-process answer
        answer = self._post_process_answer(
            answer, coverage, confidence_breakdown, risk_assessment
        )
        
        return {
            'answer': answer,
            'prompt_type': prompt_type,
            'coverage_tier': coverage['tier'],
        }
    
    def _build_user_prompt(self,
                           query: str,
                           context: Optional[str],
                           features: ClinicalFeatures,
                           risk_assessment: RiskAssessment,
                           coverage: Dict,
                           confidence_breakdown: Dict) -> str:
        """Build comprehensive user prompt."""
        parts = []
        
        # Clinical rule summary
        rule_summary = self._build_clinical_rule_summary(features)
        parts.append(rule_summary)
        parts.append("\n")
        
        # Risk assessment
        parts.append("=== RISK ASSESSMENT ===")
        parts.append(f"Risk Level: {risk_assessment.risk_level.upper()}")
        parts.append(f"Risk Score: {risk_assessment.total_score}")
        if risk_assessment.risk_factors:
            parts.append("\nRisk Factors:")
            for rf in risk_assessment.risk_factors:
                parts.append(f"  • {rf['factor']}: {rf['value']} (Score: {rf['score']})")
        parts.append("\n")
        
        # Coverage information
        parts.append("=== DOCUMENT COVERAGE ===")
        parts.append(f"Coverage Tier: {coverage['tier']}")
        parts.append(f"Derivable from Rules: {coverage['derivable']}")
        parts.append(f"Has Clinical Rules: {coverage['has_rules']}")
        parts.append(f"Covered Topics: {', '.join(coverage['covered_topics']) if coverage['covered_topics'] else 'None'}")
        parts.append("\n")
        
        # Retrieved context
        if context:
            parts.append("=== RETRIEVED CONTEXT ===")
            parts.append(context)
            parts.append("\n")
        
        # User question
        parts.append("=== USER QUESTION ===")
        parts.append(query)
        parts.append("\n")
        
        # Instructions
        parts.append("=== INSTRUCTIONS ===")
        if coverage['derivable']:
            parts.append("APPLY THE CLINICAL RULES ABOVE to answer this question.")
            parts.append("Use document thresholds to classify the patient's values.")
            parts.append("Be definitive - the rules clearly apply to this case.")
            parts.append("Format: Clinical Assessment → Risk Classification → Recommendations")
        elif coverage['has_partial']:
            parts.append("Answer based on what IS covered in the context.")
            parts.append("Clearly state what is NOT covered.")
            parts.append("Use document-grounded language with citations.")
        else:
            parts.append("Acknowledge this question is not covered in the document.")
            parts.append("Suggest related topics that ARE covered.")
        
        parts.append("\nYour response:")
        
        return "\n".join(parts)
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Call Ollama API."""
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS,
                "top_p": 1.0,
                "repeat_penalty": 1.1,
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
            raise ConnectionError(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out")
    
    def _post_process_answer(self,
                             answer: str,
                             coverage: Dict,
                             confidence_breakdown: Dict,
                             risk_assessment: RiskAssessment) -> str:
        """Post-process answer with confidence badges."""
        # Add confidence badge based on coverage
        if coverage['derivable']:
            confidence_score = confidence_breakdown['retrieval_quality'] * 0.4 + \
                              confidence_breakdown['rule_coverage'] * 0.3 + \
                              confidence_breakdown['chunk_agreement'] * 0.3
            answer += f"\n\n✅ [HIGH CONFIDENCE — Derived from document thresholds and rules]"
            answer += f"\n   Confidence Score: {confidence_score:.2f}"
            answer += f"\n   - Retrieval Quality: {confidence_breakdown['retrieval_quality']:.2f}"
            answer += f"\n   - Rule Coverage: {confidence_breakdown['rule_coverage']:.2f}"
            answer += f"\n   - Chunk Agreement: {confidence_breakdown['chunk_agreement']:.2f}"
        elif coverage['has_rules']:
            answer += f"\n\n⚠️ [MEDIUM CONFIDENCE — Based on document rules with partial coverage]"
        elif coverage['has_partial']:
            answer += f"\n\n ℹ️ [LOW CONFIDENCE — Partial document coverage]"
        else:
            answer += f"\n\n❌ [NO COVERAGE — Question not addressed in document]"
        
        # Add clinical warning if high-risk
        if risk_assessment.risk_level in ['high', 'critical']:
            answer += f"\n\n🚨 [HIGH-RISK PREGNANCY — Specialist consultation required]"
        
        return answer
