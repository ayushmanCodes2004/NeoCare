# ============================================================
# layer4_reasoning.py — Evidence-Grounded Reasoning
# ============================================================
"""
LAYER 4: Evidence-Grounded Reasoning

LLM reasons ONLY from:
- Retrieved chunks (with page citations)
- Rule engine output

If evidence missing: Return "NOT FOUND IN DOCUMENT"
No hallucinations allowed.
"""

import requests
from typing import Dict
from layer1_extractor import ClinicalFeatures
from clinical_rules import RuleEngineResult  # Using pre-RAG rule engine
from evidence_attribution import EvidenceAttributor
from config_production import (
    OLLAMA_BASE_URL, OLLAMA_MODEL, TEMPERATURE,
    MAX_TOKENS, MEDICAL_DISCLAIMER
)


class EvidenceGroundedReasoner:
    """
    Evidence-grounded LLM reasoning with strict hallucination prevention.
    """
    
    SYSTEM_PROMPT = """You are a clinical decision-support assistant specialized in Antenatal Care (ANC) for maternal health in India. You assist frontline health workers (ANMs, ASHAs) and PHC/CHC doctors by explaining High-Pregnancy-Risk (HPR) assessments in a clear, evidence-based, and actionable manner.

---

## YOUR ROLE

You do NOT diagnose or re-calculate risk. The HPR classification has already been determined by a validated deterministic rule engine based on GoI High-Risk Pregnancy Guidelines. Your job is to:

1. Explain WHY the patient has been classified at the given risk level, referencing her specific clinical values.
2. Summarize the key driving factors behind the classification.
3. Provide appropriate care guidance aligned with the risk level and care setting.
4. Flag any values that are borderline or require monitoring even if they did not trigger HPR alone.
5. Use simple, professional language suitable for a PHC-level health worker or doctor.

---

## INPUT CONTEXT YOU WILL RECEIVE

Each query will include:
- **Clinical Query**: A narrative summary of the patient's condition
- **Extracted Features**: Structured clinical data (age, GA, vitals, labs, etc.)
- **Rule Engine Output**: The deterministic HPR result including:
  - `risk_level`: "LOW", "MODERATE", "HIGH", or "CRITICAL"
  - `risk_score`: Numeric score (0-2=LOW, 3-5=MODERATE, 6-8=HIGH, 9+=CRITICAL)
  - `triggered_rules`: List of specific conditions detected
  - `confirmed_conditions`: Conditions with lab confirmation
  - `suspected_conditions`: Conditions needing confirmatory tests
  - `referral_facility`: Recommended facility level
- **Retrieved Evidence**: Relevant chunks from GoI guidelines with page citations
- **Care Level**: Facility level (ASHA/PHC/CHC/DISTRICT)

---

## HOW TO STRUCTURE YOUR RESPONSE

### 1. Risk Classification Summary
State the risk level clearly and confidently. Do not hedge or re-evaluate it.

Example: "Based on the deterministic risk engine, this patient has been classified as **[RISK LEVEL]** with a risk score of [X]."

### 2. Key Drivers of Classification
Explain each triggered condition in plain clinical language. Reference the patient's actual values:
- Mention what the normal/threshold range is
- Mention what the patient's value is
- Explain why it matters clinically

Example:
"The classification is driven by:
1. **Mild Anaemia**: Hemoglobin 10.6 g/dL (threshold: <11 g/dL). While not severe, this requires iron supplementation.
2. **GDM Screening Pending**: At 20 weeks gestation, 75g OGTT screening is due (should be done between 14-28 weeks per GoI guidelines)."

### 3. Borderline or Watch-Out Values
Even if a value did not trigger HPR, flag anything that is close to a threshold or requires monitoring.

Example: "Blood pressure 110/72 mmHg is normal, but monitor at each visit as hypertension threshold is 140/90 mmHg."

### 4. Recommended Actions
Suggest concrete next steps appropriate to the care level and risk classification:
- **Investigations to order**: Specify tests needed
- **Treatment**: Standard protocols (IFA, antihypertensives, etc.) with dosages per GoI guidelines
- **Referral guidance**: When and where to refer
- **Counseling points**: What to tell the patient
- **Follow-up frequency**: Based on risk level

### 5. Reassurance Points (for Low/Moderate Risk)
If the patient is not high risk, clearly affirm what is going well clinically to reassure the health worker and patient.

Example: "Positive findings: Normal blood pressure, no proteinuria, appropriate gestational age, no danger signs present."

---

## TONE AND LANGUAGE GUIDELINES

- Be clinical but accessible — write for a trained ANM or PHC doctor, not a specialist
- Never speculate beyond the provided data
- Never contradict the HPR classification produced by the engine
- If a triggered flag seems inconsistent with the data provided, note it respectfully as "please verify this value" rather than overriding the engine
- Keep responses focused and structured — avoid long-winded paragraphs
- Always cite page numbers when referencing GoI guidelines

---

## CRITICAL CONSTRAINTS

- You MUST base your explanation strictly on the rule engine output and retrieved evidence provided
- You must NOT invent or assume clinical values not present in the input
- You must NOT re-run or second-guess the risk classification logic
- You must NOT provide dosage recommendations unless they are standard national protocol (e.g., IFA supplementation per MoHFW India guidelines)
- Always respect the care_level — do not recommend investigations or interventions unavailable at that facility level without pairing it with a referral recommendation

---

## KNOWLEDGE BASE

Your responses should be grounded in:
- MoHFW India ANC guidelines (LaQshya, SUMAN, RCH protocols)
- GoI High-Risk Pregnancy Guidelines (clinical_thresholds.md)
- Standard threshold values for Indian obstetric context:
  - Anaemia: Hb <11 g/dL (Mild: 10-10.9, Moderate: 7-9.9, Severe: <7)
  - Hypertension: BP ≥140/90 mmHg
  - GDM: 2hr PG ≥140 mg/dL on 75g OGTT
  - Age: <20 years (young primi) or ≥35 years (advanced maternal age)

---

## EXAMPLE TRIGGERED CONDITIONS

| Condition | Clinical Meaning | Score |
|-----------|------------------|-------|
| `mild_anaemia` | Hb 10–10.9 g/dL | 1 |
| `moderate_anaemia` | Hb 7–9.9 g/dL | 2 |
| `severe_anaemia` | Hb <7 g/dL | 4 |
| `hypertension` | BP ≥140/90 mmHg | 3 |
| `pre_eclampsia` | BP ≥140/90 + proteinuria | 3 |
| `gdm_confirmed` | 2hr PG ≥140 mg/dL | 2 |
| `gdm_screening_pending` | No OGTT done, GA 14-28 weeks | 1 |
| `young_primi` | Age <20 years | 3 |
| `advanced_maternal_age` | Age ≥35 years | 3 |
| `twin_pregnancy` | Multiple gestation | 3 |
| `previous_cs` | Prior cesarean section | 2 |
| `placenta_previa` | Confirmed or suspected | 4 |
| `short_stature` | Height <140 cm | 2 |
| `high_bmi` | BMI ≥30 kg/m² | 2 |
| `smoking` | Current smoker | 2 |
| `tobacco_use` | Tobacco use | 2 |
| `alcohol_use` | Alcohol consumption | 2 |
| `high_birth_order` | Birth order ≥5 | 2 |
| `short_birth_spacing` | Inter-pregnancy interval <18 months | 2 |
| `long_birth_spacing` | Inter-pregnancy interval >59 months | 1 |
| `previous_preterm` | History of preterm delivery | 2 |
| `previous_stillbirth` | History of stillbirth | 2 |
| `previous_abortion` | History of abortion | 2 |
| `rh_negative` | Rh negative blood group | 1 |
| `hiv_positive` | HIV positive | 3 |
| `syphilis_positive` | Syphilis positive | 3 |
| `malpresentation` | Abnormal fetal presentation | 2 |
| `systemic_illness` | Current or past systemic illness | 2 |

---

## IMPORTANT REMINDERS

- The risk score and classification are FINAL — your job is to EXPLAIN, not recalculate
- Always reference the patient's actual clinical values when explaining
- Provide actionable guidance appropriate to the care level
- Be reassuring when appropriate, but never minimize genuine risks
- Cite page numbers from GoI guidelines when making recommendations

Begin your response only after receiving the full patient context and rule engine output."""

    def __init__(self):
        """Initialize reasoner (evidence attributor created per-request with rule_output)."""
        pass
    
    def generate_response(self,
                          query: str,
                          features: ClinicalFeatures,
                          rule_output: RuleEngineOutput,
                          retrieval_result: Dict,
                          confidence: Dict,
                          care_level: str = 'PHC',
                          verbose: bool = False) -> str:
        """
        Generate evidence-grounded response with care-level awareness.
        
        Args:
            query: Original user query
            features: Extracted clinical features
            rule_output: Rule engine output
            retrieval_result: Retrieval results with chunks
            confidence: Confidence scores
            care_level: Care level context ('ASHA', 'PHC', 'CHC', 'DISTRICT')
            verbose: Print generation details
            
        Returns:
            Formatted clinical response
        """
        if verbose:
            print("\n[REASONING] Generating evidence-grounded response...")
            print(f"[REASONING] Care level: {care_level}")
        
        # Build prompt
        user_prompt = self._build_prompt(
            query, features, rule_output, retrieval_result, confidence, care_level
        )
        
        # Call LLM
        answer = self._call_llm(self.SYSTEM_PROMPT, user_prompt)
        
        # CRITICAL: Validate clinical reasoning rules
        answer = self._validate_clinical_reasoning(
            answer, features, rule_output, verbose
        )
        
        # CRITICAL: Apply care-level filtering
        answer = self._filter_by_care_level(answer, care_level, verbose)
        
        # CRITICAL: Verify evidence grounding with severity constraints
        attributor = EvidenceAttributor(rule_output=rule_output)
        grounding_result = attributor.verify_grounding(
            answer,
            retrieval_result.get('chunks', []),
            verbose=verbose
        )
        
        # Clean output if needed
        if not grounding_result['is_safe']:
            if verbose:
                print(f"[REASONING] ⚠️  Cleaning {grounding_result['ungrounded_claims']} ungrounded claims")
            answer = attributor.clean_output(answer, grounding_result)
        
        # Format final output
        formatted = self._format_output(
            answer, rule_output, confidence, retrieval_result, grounding_result, care_level
        )
        
        return formatted
    
    def _build_prompt(self,
                      query: str,
                      features: ClinicalFeatures,
                      rule_output: RuleEngineResult,
                      retrieval_result: Dict,
                      confidence: Dict,
                      care_level: str) -> str:
        """Build comprehensive prompt with all evidence and care-level context."""
        from config_production import CARE_LEVELS
        
        parts = []
        
        # Section 0: Care Level Context
        care_info = CARE_LEVELS.get(care_level, CARE_LEVELS['PHC'])
        parts.append("=== CARE LEVEL CONTEXT ===")
        parts.append(f"Setting: {care_info['name']}")
        parts.append(f"Allowed Actions: {', '.join(care_info['allowed_actions'])}")
        if care_info['forbidden_treatments']:
            parts.append(f"NOT Available at This Level: {', '.join(care_info['forbidden_treatments'])}")
        parts.append("")
        parts.append("IMPORTANT: Recommendations must be appropriate for this care level.")
        parts.append("If advanced treatment needed, recommend REFERRAL to higher center.")
        parts.append("")
        
        # Section 1: Clinical Rules (Authoritative)
        parts.append("=== CLINICAL RULES (AUTHORITATIVE) ===")
        parts.append(f"Overall Risk: {rule_output.risk_level}")
        parts.append(f"Total Risk Score: {rule_output.risk_score}")
        parts.append("")
        
        # List CONFIRMED conditions based on triggered rules
        parts.append("CONFIRMED CONDITIONS (from clinical rules):")
        confirmed_conditions = []
        if rule_output.risk_flags:
            for flag in rule_output.risk_flags:
                confirmed_conditions.append(flag.get('condition', ''))
                parts.append(f"  • {flag.get('condition', '')}: {flag.get('present', False)}")
                parts.append(f"    Value: {flag.get('value', '')}")
                parts.append(f"    Threshold: {flag.get('threshold', 'N/A')}")
                parts.append(f"    Severity: {flag.get('severity', '')}")
                if 'rationale' in flag:
                    parts.append(f"    Rationale: {flag['rationale']}")
                parts.append("")
        else:
            parts.append("  • No risk flags triggered (all parameters within normal limits)")
            parts.append("")
        
        # CRITICAL: List conditions to check for topic isolation
        parts.append("TOPIC ISOLATION CHECK:")
        parts.append("Only use retrieved chunks if their topic matches one of the CONFIRMED CONDITIONS above.")
        parts.append("Example: If patient does NOT have confirmed GDM/Diabetes, do NOT use chunks from GDM section.")
        parts.append("")
        
        # Section 2: Extracted Features
        parts.append("=== EXTRACTED CLINICAL FEATURES ===")
        if features.age:
            parts.append(f"Age: {features.age} years")
        if features.gestational_age_weeks:
            parts.append(f"Gestational Age: {features.gestational_age_weeks} weeks")
        if features.systolic_bp and features.diastolic_bp:
            parts.append(f"Blood Pressure: {features.systolic_bp}/{features.diastolic_bp} mmHg")
        if features.hemoglobin:
            parts.append(f"Hemoglobin: {features.hemoglobin} g/dL")
        if features.fbs:
            parts.append(f"Fasting Blood Sugar: {features.fbs} mg/dL")
        if features.twin_pregnancy:
            parts.append("Twin Pregnancy: Yes")
        if features.prior_cesarean:
            parts.append("Previous Cesarean: Yes")
        if features.placenta_previa:
            parts.append("Placenta Previa: Yes")
        if features.comorbidities:
            parts.append(f"Comorbidities: {', '.join(features.comorbidities)}")
        parts.append("")
        
        # Section 3: Retrieved Document Evidence
        parts.append("=== RETRIEVED DOCUMENT EVIDENCE ===")
        chunks = retrieval_result.get('chunks', [])
        if chunks:
            for rank, (doc, score) in enumerate(chunks, 1):
                meta = doc.metadata
                parts.append(f"[Evidence {rank} | Page {meta.get('page_number', '?')} | Score: {score:.3f}]")
                parts.append(doc.page_content)
                parts.append("")
        else:
            parts.append("No relevant document evidence retrieved.")
            parts.append("")
        
        # Section 4: User Question
        parts.append("=== USER QUESTION ===")
        parts.append(query)
        parts.append("")
        
        # Section 5: Instructions
        parts.append("=== INSTRUCTIONS ===")
        parts.append("Generate a response in the following format:")
        parts.append("")
        parts.append("Risk Classification:")
        parts.append("- [List each risk factor with Present/Absent status]")
        parts.append("")
        parts.append(f"Overall Risk: [LOW/MODERATE/HIGH/CRITICAL] (rule-based)")
        parts.append(f"Risk Score: {rule_output.risk_score}")
        parts.append("")
        parts.append("Evidence:")
        parts.append("- Page X: [specific finding from document]")
        parts.append("- Page Y: [specific finding from document]")
        parts.append("")
        parts.append("Clinical Recommendations:")
        parts.append("- [Evidence-based recommendations from document]")
        parts.append("")
        
        # Add specific drug guidance for hypertension
        if any('hypertension' in rule.lower() for rule in rule_output.triggered_rules):
            parts.append("MANDATORY FOR HYPERTENSION:")
            parts.append("Include antihypertensive drug options:")
            parts.append("- First line: Tab Alpha Methyl Dopa 250mg BD/TDS")
            parts.append("- Second line: Nifedipine 10-20mg orally BD/TDS")
            parts.append("- Third line: Labetalol 100mg BD")
            parts.append("")
        
        # Add steroid gating check
        if features.gestational_age_weeks:
            if 24 <= features.gestational_age_weeks <= 34:
                parts.append("ANTENATAL STEROIDS:")
                parts.append("Recommend Inj. Dexamethasone 6mg IM 12-hourly x2 days ONLY if:")
                parts.append("- Preterm delivery is being actively planned OR")
                parts.append("- IUGR is suspected")
                parts.append("Do NOT recommend steroids without these indications.")
                parts.append("")
        
        parts.append("CRITICAL VALIDATION CHECKS:")
        parts.append("1. Topic Isolation: Only use chunks matching CONFIRMED CONDITIONS")
        parts.append("2. Drug Completeness: Include all relevant drug options for confirmed conditions")
        parts.append("3. Steroid Gating: Only recommend if GA 24-34 weeks + preterm delivery planned")
        parts.append(f"4. Consistency: Risk Score in answer MUST match {rule_output.risk_score}")
        parts.append("5. Citation Validity: Only cite pages for patient's confirmed conditions")
        parts.append("6. Differential Clarity: State 'Suspected [condition]' if confirmatory test unavailable")
        parts.append("")
        parts.append("IMPORTANT:")
        parts.append("- Use ONLY the clinical rules and document evidence provided above")
        parts.append("- Cite page numbers for all document-based claims")
        parts.append("- If information is not in the evidence, state 'NOT FOUND IN DOCUMENT'")
        parts.append("- Do NOT fabricate or speculate")
        parts.append("")
        parts.append("Your response:")
        
        return "\n".join(parts)
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call Ollama LLM."""
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
        except Exception as e:
            return f"ERROR: Failed to generate response - {str(e)}"
    
    def _validate_clinical_reasoning(self,
                                     answer: str,
                                     features: ClinicalFeatures,
                                     rule_output: RuleEngineResult,
                                     verbose: bool) -> str:
        """
        Validate clinical reasoning rules compliance.
        
        Checks:
        1. Drug completeness for hypertension
        2. Steroid gating (only if GA 24-34 weeks + indication)
        3. Risk score consistency
        """
        answer_lower = answer.lower()
        warnings = []
        
        # Rule 2: Drug Recommendation Completeness for Hypertension
        has_hypertension = any('hypertension' in rule.lower() for rule in rule_output.triggered_rules)
        if has_hypertension:
            # Check if antihypertensive drugs mentioned
            has_methyldopa = 'methyldopa' in answer_lower or 'alpha methyl dopa' in answer_lower
            has_nifedipine = 'nifedipine' in answer_lower
            has_labetalol = 'labetalol' in answer_lower
            
            if not (has_methyldopa or has_nifedipine or has_labetalol):
                warnings.append("⚠️ VALIDATION: Hypertension detected but no antihypertensive drugs mentioned")
                if verbose:
                    print(f"[REASONING] ⚠️ Drug completeness check failed for hypertension")
                
                # Add drug guidance
                drug_guidance = "\n\nAntihypertensive Options:\n"
                drug_guidance += "- First line: Tab Alpha Methyl Dopa 250mg BD/TDS\n"
                drug_guidance += "- Second line: Nifedipine 10-20mg orally BD/TDS\n"
                drug_guidance += "- Third line: Labetalol 100mg BD"
                answer += drug_guidance
        
        # Rule 3: Antenatal Steroids Gating
        has_steroids = 'dexamethasone' in answer_lower or 'antenatal steroid' in answer_lower
        if has_steroids:
            ga = features.gestational_age_weeks
            if ga is None or ga < 24 or ga > 34:
                warnings.append(f"⚠️ VALIDATION: Steroids recommended but GA={ga} (should be 24-34 weeks)")
                if verbose:
                    print(f"[REASONING] ⚠️ Steroid gating check failed: GA={ga}")
        
        # Rule 4: Internal Consistency (Risk Score)
        # Extract risk score from answer if present
        import re
        score_pattern = r'(?:risk\s+score|score)[:\s]+(\d+)'
        matches = re.findall(score_pattern, answer_lower)
        if matches:
            answer_score = int(matches[0])
            if answer_score != rule_output.risk_score:
                warnings.append(f"⚠️ VALIDATION: Risk score mismatch (answer={answer_score}, actual={rule_output.risk_score})")
                if verbose:
                    print(f"[REASONING] ⚠️ Consistency check failed: score mismatch")
                
                # Fix the score in answer
                answer = re.sub(
                    r'((?:risk\s+score|score)[:\s]+)\d+',
                    f'\\g<1>{rule_output.risk_score}',
                    answer,
                    flags=re.IGNORECASE
                )
        
        if warnings and verbose:
            print(f"[REASONING] Validation warnings: {len(warnings)}")
        
        return answer
    
    def _filter_by_care_level(self, answer: str, care_level: str, verbose: bool) -> str:
        """
        Filter recommendations by care level.
        Remove specialist treatments not available at current level.
        """
        from config_production import CARE_LEVELS, SPECIALIST_TREATMENTS
        
        care_info = CARE_LEVELS.get(care_level, CARE_LEVELS['PHC'])
        forbidden = care_info.get('forbidden_treatments', [])
        
        if not forbidden:
            return answer  # District level - no filtering
        
        # Check for forbidden treatments in answer
        answer_lower = answer.lower()
        violations_found = []
        
        for treatment in SPECIALIST_TREATMENTS:
            if treatment in answer_lower:
                # Check if this treatment is forbidden at current level
                if any(forbidden_term in treatment for forbidden_term in forbidden):
                    violations_found.append(treatment)
        
        if violations_found and verbose:
            print(f"[REASONING] ⚠️  Care-level violations found: {violations_found}")
            print(f"[REASONING] Adding referral guidance...")
        
        # If violations found, add referral guidance
        if violations_found:
            referral_note = f"\n\n⚠️ NOTE: Advanced treatments mentioned above require referral to higher center (CHC/District Hospital).\nAt {care_info['name']} level: Stabilize patient and arrange immediate referral."
            answer += referral_note
        
        return answer
    
    def _format_output(self,
                       answer: str,
                       rule_output: RuleEngineResult,
                       confidence: Dict,
                       retrieval_result: Dict,
                       grounding_result: Dict,
                       care_level: str) -> str:
        """Format final output with medical disclaimer, confidence, and grounding info."""
        from config_production import CARE_LEVELS
        
        output = []
        
        # Medical disclaimer
        output.append(MEDICAL_DISCLAIMER)
        output.append("")
        
        # Care level context
        care_info = CARE_LEVELS.get(care_level, CARE_LEVELS['PHC'])
        output.append(f"Care Level: {care_info['name']}")
        output.append("")
        
        # Add urgent warning for critical/high risk
        if rule_output.risk_level in ['CRITICAL', 'HIGH']:
            output.append("⚠️ URGENT: Refer to obstetric specialist immediately")
            output.append("⚠️ HIGH-RISK PREGNANCY — Requires enhanced surveillance")
            output.append("")
        
        output.append("="*70)
        output.append("")
        
        # Main answer
        output.append(answer)
        output.append("")
        output.append("="*70)
        output.append("")
        
        # Evidence grounding info
        if grounding_result['grounding_score'] < 1.0:
            output.append(f"Evidence Grounding: {grounding_result['grounding_score']:.2f}")
            output.append(f"  - Grounded claims: {grounding_result['grounded_claims']}/{grounding_result['total_claims']}")
            if grounding_result['ungrounded_claims'] > 0:
                output.append(f"  - ⚠️  Ungrounded claims removed: {grounding_result['ungrounded_claims']}")
            output.append("")
        
        # Confidence breakdown (STRICT MAPPING)
        conf_score = confidence['score']
        if conf_score >= 0.85:
            conf_label = "HIGH"
        elif conf_score >= 0.60:
            conf_label = "MEDIUM"
        else:
            conf_label = "LOW"
        
        output.append(f"Confidence: {conf_score:.2f} ({conf_label})")
        output.append("")
        output.append("Confidence Breakdown:")
        breakdown = confidence['breakdown']
        output.append(f"  - Retrieval Quality: {breakdown['retrieval_quality']:.2f}")
        output.append(f"  - Rule Coverage: {breakdown['rule_coverage']:.2f}")
        output.append(f"  - Chunk Agreement: {breakdown['chunk_agreement']:.2f}")
        output.append(f"  - Extractor Confidence: {breakdown['extractor_confidence']:.2f}")
        output.append("")
        
        # Retrieval stats
        output.append("Retrieval Statistics:")
        output.append(f"  - FAISS chunks: {retrieval_result.get('faiss_count', 0)}")
        output.append(f"  - BM25 chunks: {retrieval_result.get('bm25_count', 0)}")
        output.append(f"  - Final chunks: {retrieval_result.get('final_count', 0)}")
        output.append("")
        
        # Final disclaimer
        output.append("[Consult qualified physician for all clinical decisions]")
        
        return "\n".join(output)
