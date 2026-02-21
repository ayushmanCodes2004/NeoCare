# ============================================================
# diagnosis_confidence_gate.py — Step 5.5: Diagnosis Confidence Gate
# ============================================================
"""
STEP 5.5: Diagnosis Confidence Gate

Downgrades diagnoses from "confirmed" to "suspected" when confirmatory tests unavailable.

Clinical Logic:
- Pre-eclampsia requires: BP ≥140/90 AND proteinuria
  → If proteinuria unknown → "Suspected pre-eclampsia"
  
- GDM requires: Abnormal OGTT
  → If OGTT not done → "Cannot confirm GDM"
  
- Eclampsia requires: Seizures
  → If no seizures → "Not eclampsia"

Prevents false positive diagnoses and maintains clinical honesty.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DiagnosisConfidence:
    """Diagnosis with confidence level."""
    condition: str
    status: str  # 'confirmed', 'suspected', 'ruled_out', 'cannot_assess'
    reason: str
    required_tests: List[str]
    available_tests: List[str]
    confidence: float  # 0.0 to 1.0


class DiagnosisConfidenceGate:
    """
    Validates diagnoses against available confirmatory tests.
    Downgrades to 'suspected' when tests unavailable.
    """
    
    # Diagnostic criteria for each condition
    DIAGNOSTIC_CRITERIA = {
        'pre_eclampsia': {
            'required': ['hypertension', 'proteinuria'],
            'tests': {
                'hypertension': 'BP measurement',
                'proteinuria': 'Urine dipstick or 24h protein'
            },
            'partial_diagnosis': 'suspected_pre_eclampsia'
        },
        'severe_pre_eclampsia': {
            'required': ['severe_hypertension', 'proteinuria'],
            'tests': {
                'severe_hypertension': 'BP ≥160/110',
                'proteinuria': 'Urine dipstick 3+ or 4+'
            },
            'partial_diagnosis': 'suspected_severe_pre_eclampsia'
        },
        'eclampsia': {
            'required': ['pre_eclampsia', 'seizures'],
            'tests': {
                'pre_eclampsia': 'BP + proteinuria',
                'seizures': 'Witnessed seizure activity'
            },
            'partial_diagnosis': 'pre_eclampsia_without_seizures'
        },
        'gdm': {
            'required': ['abnormal_ogtt'],
            'tests': {
                'abnormal_ogtt': 'OGTT ≥92 mg/dL (fasting) or ≥153 (1h) or ≥140 (2h)'
            },
            'partial_diagnosis': 'elevated_fbs_needs_ogtt'
        },
        'overt_diabetes': {
            'required': ['very_high_glucose'],
            'tests': {
                'very_high_glucose': 'FBS ≥126 mg/dL or Random ≥200 mg/dL'
            },
            'partial_diagnosis': 'suspected_diabetes'
        },
        'severe_anemia': {
            'required': ['hemoglobin_test'],
            'tests': {
                'hemoglobin_test': 'Hb <7 g/dL'
            },
            'partial_diagnosis': None  # Hb test is definitive
        },
        'iugr': {
            'required': ['ultrasound'],
            'tests': {
                'ultrasound': 'USG showing fetal weight <10th percentile'
            },
            'partial_diagnosis': 'suspected_iugr_by_sfh'
        }
    }
    
    def __init__(self, verbose: bool = False):
        """Initialize diagnosis confidence gate."""
        self.verbose = verbose
    
    def validate_diagnosis(self,
                          condition: str,
                          clinical_findings: Dict,
                          available_tests: List[str]) -> DiagnosisConfidence:
        """
        Validate a diagnosis against available confirmatory tests.
        
        Args:
            condition: Proposed diagnosis
            clinical_findings: Dict of clinical findings (BP, Hb, etc.)
            available_tests: List of tests that were performed
            
        Returns:
            DiagnosisConfidence with status and reasoning
        """
        if condition not in self.DIAGNOSTIC_CRITERIA:
            # Unknown condition, cannot validate
            return DiagnosisConfidence(
                condition=condition,
                status='cannot_assess',
                reason='Diagnostic criteria not defined',
                required_tests=[],
                available_tests=available_tests,
                confidence=0.5
            )
        
        criteria = self.DIAGNOSTIC_CRITERIA[condition]
        required = criteria['required']
        tests = criteria['tests']
        
        # Check which required criteria are met
        met_criteria = []
        missing_criteria = []
        
        for criterion in required:
            if self._is_criterion_met(criterion, clinical_findings, available_tests):
                met_criteria.append(criterion)
            else:
                missing_criteria.append(criterion)
        
        # Determine status
        if len(met_criteria) == len(required):
            # All criteria met - confirmed diagnosis
            status = 'confirmed'
            confidence = 0.95
            reason = f"All diagnostic criteria met: {', '.join(met_criteria)}"
        elif len(met_criteria) > 0:
            # Some criteria met - suspected diagnosis
            status = 'suspected'
            confidence = 0.6
            partial_condition = criteria.get('partial_diagnosis', f'suspected_{condition}')
            reason = f"Partial criteria met: {', '.join(met_criteria)}. Missing: {', '.join(missing_criteria)}"
        else:
            # No criteria met - ruled out
            status = 'ruled_out'
            confidence = 0.1
            reason = f"Diagnostic criteria not met. Missing: {', '.join(missing_criteria)}"
        
        if self.verbose:
            print(f"[DIAGNOSIS GATE] {condition}: {status} (confidence: {confidence:.2f})")
            print(f"[DIAGNOSIS GATE] Reason: {reason}")
        
        return DiagnosisConfidence(
            condition=condition if status == 'confirmed' else criteria.get('partial_diagnosis', f'suspected_{condition}'),
            status=status,
            reason=reason,
            required_tests=[tests[c] for c in required],
            available_tests=available_tests,
            confidence=confidence
        )
    
    def _is_criterion_met(self,
                         criterion: str,
                         clinical_findings: Dict,
                         available_tests: List[str]) -> bool:
        """
        Check if a specific diagnostic criterion is met.
        
        Args:
            criterion: Criterion name
            clinical_findings: Clinical data
            available_tests: Tests performed
            
        Returns:
            True if criterion is met
        """
        # Hypertension criteria
        if criterion == 'hypertension':
            bp_systolic = clinical_findings.get('systolic_bp')
            bp_diastolic = clinical_findings.get('diastolic_bp')
            return (bp_systolic and bp_systolic >= 140) or (bp_diastolic and bp_diastolic >= 90)
        
        if criterion == 'severe_hypertension':
            bp_systolic = clinical_findings.get('systolic_bp')
            bp_diastolic = clinical_findings.get('diastolic_bp')
            return (bp_systolic and bp_systolic >= 160) or (bp_diastolic and bp_diastolic >= 110)
        
        # Proteinuria
        if criterion == 'proteinuria':
            return 'urine_dipstick' in available_tests and clinical_findings.get('proteinuria', False)
        
        # Seizures
        if criterion == 'seizures':
            return clinical_findings.get('seizures', False) or clinical_findings.get('convulsions', False)
        
        # Pre-eclampsia (composite)
        if criterion == 'pre_eclampsia':
            has_hypertension = self._is_criterion_met('hypertension', clinical_findings, available_tests)
            has_proteinuria = self._is_criterion_met('proteinuria', clinical_findings, available_tests)
            return has_hypertension and has_proteinuria
        
        # Glucose criteria
        if criterion == 'abnormal_ogtt':
            return 'ogtt' in available_tests and clinical_findings.get('ogtt_abnormal', False)
        
        if criterion == 'very_high_glucose':
            fbs = clinical_findings.get('fbs')
            return fbs and fbs >= 126
        
        # Hemoglobin
        if criterion == 'hemoglobin_test':
            hb = clinical_findings.get('hemoglobin')
            return hb is not None  # Test was done
        
        # Ultrasound
        if criterion == 'ultrasound':
            return 'ultrasound' in available_tests
        
        return False
    
    def apply_confidence_gating(self,
                                detected_conditions: List[str],
                                clinical_findings: Dict,
                                available_tests: List[str]) -> Dict[str, DiagnosisConfidence]:
        """
        Apply confidence gating to all detected conditions.
        
        Args:
            detected_conditions: List of detected condition names
            clinical_findings: Clinical data
            available_tests: Tests performed
            
        Returns:
            Dict mapping condition to DiagnosisConfidence
        """
        results = {}
        
        for condition in detected_conditions:
            # Normalize condition name
            condition_normalized = condition.lower().replace(' ', '_').replace('-', '_')
            
            # Validate
            diagnosis = self.validate_diagnosis(
                condition_normalized,
                clinical_findings,
                available_tests
            )
            
            results[condition] = diagnosis
        
        return results


def apply_diagnosis_confidence_gate(detected_conditions: List[str],
                                    clinical_findings: Dict,
                                    query: str,
                                    verbose: bool = False) -> Dict[str, DiagnosisConfidence]:
    """
    Convenience function to apply diagnosis confidence gate.
    
    Args:
        detected_conditions: List of detected conditions
        clinical_findings: Clinical data (BP, Hb, etc.)
        query: Original query to infer available tests
        verbose: Print validation details
        
    Returns:
        Dict of validated diagnoses with confidence levels
    """
    # Infer available tests from query
    query_lower = query.lower()
    available_tests = []
    
    if 'urine' in query_lower or 'dipstick' in query_lower or 'proteinuria' in query_lower:
        available_tests.append('urine_dipstick')
    if 'ogtt' in query_lower:
        available_tests.append('ogtt')
    if 'ultrasound' in query_lower or 'usg' in query_lower:
        available_tests.append('ultrasound')
    if 'hb' in query_lower or 'hemoglobin' in query_lower or 'haemoglobin' in query_lower:
        available_tests.append('hemoglobin')
    
    # Check for explicit "unavailable" mentions
    if 'no urine' in query_lower or 'urine unavailable' in query_lower or 'dipstick unavailable' in query_lower:
        available_tests = [t for t in available_tests if t != 'urine_dipstick']
    if 'no ultrasound' in query_lower or 'usg unavailable' in query_lower or 'usg not available' in query_lower:
        available_tests = [t for t in available_tests if t != 'ultrasound']
    
    gate = DiagnosisConfidenceGate(verbose=verbose)
    return gate.apply_confidence_gating(detected_conditions, clinical_findings, available_tests)
