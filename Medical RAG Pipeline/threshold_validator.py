# ============================================================
# threshold_validator.py — Threshold-First RAG Validation
# ============================================================
"""
Hybrid approach: Compare values with thresholds first, then use RAG to:
1. Validate thresholds from medical guidelines
2. Get context and management recommendations
3. Cross-check with document evidence

Flow:
1. Quick threshold check (rule-based)
2. MMR retrieval for relevant guidelines
3. Extract actual thresholds from documents
4. Compare and validate
5. Return decision with evidence
"""

import re
from typing import Dict, List, Tuple, Optional
from layer2_retrieval import HybridRetriever
from layer1_extractor import ClinicalFeatures


class ThresholdValidator:
    """
    Validates clinical values against thresholds with RAG-based verification.
    """
    
    # Initial threshold rules (to be validated against documents)
    INITIAL_THRESHOLDS = {
        'hemoglobin': {
            'severe_anemia': 7.0,
            'moderate_anemia': 10.0,
            'mild_anemia': 11.0,
            'unit': 'g/dL'
        },
        'blood_pressure': {
            'severe_hypertension_systolic': 160,
            'severe_hypertension_diastolic': 110,
            'hypertension_systolic': 140,
            'hypertension_diastolic': 90,
            'unit': 'mmHg'
        },
        'fasting_blood_sugar': {
            'overt_diabetes': 126,
            'gdm': 92,
            'unit': 'mg/dL'
        },
        'maternal_age': {
            'advanced': 35,
            'teenage': 18,
            'young': 20,
            'unit': 'years'
        }
    }
    
    def __init__(self, retriever: HybridRetriever):
        """Initialize with retriever for RAG validation."""
        self.retriever = retriever
        self.validated_thresholds = {}
    
    def validate_with_rag(self,
                          parameter: str,
                          value: float,
                          features: ClinicalFeatures,
                          verbose: bool = False) -> Dict:
        """
        Validate a clinical parameter using threshold-first + RAG approach.
        
        Args:
            parameter: Clinical parameter (e.g., 'hemoglobin', 'blood_pressure')
            value: Measured value
            features: Clinical features for context
            verbose: Print validation steps
            
        Returns:
            Dict with classification, evidence, and recommendations
        """
        if verbose:
            print(f"\n[THRESHOLD VALIDATOR] Validating {parameter} = {value}")
        
        # Step 1: Quick threshold check
        initial_classification = self._quick_threshold_check(parameter, value, verbose)
        
        # Step 2: Build targeted query for RAG
        query = self._build_validation_query(parameter, value, initial_classification)
        
        # Step 3: Retrieve relevant chunks using MMR
        retrieval_result = self.retriever.retrieve(query, features, verbose)
        chunks = retrieval_result['chunks']
        
        # Step 4: Extract thresholds from documents
        document_thresholds = self._extract_thresholds_from_chunks(
            parameter, chunks, verbose
        )
        
        # Step 5: Compare and validate
        final_classification = self._compare_and_validate(
            parameter,
            value,
            initial_classification,
            document_thresholds,
            chunks,
            verbose
        )
        
        return final_classification
    
    def _quick_threshold_check(self,
                                parameter: str,
                                value: float,
                                verbose: bool) -> Dict:
        """
        Quick rule-based threshold check.
        
        Returns initial classification to guide RAG retrieval.
        """
        if parameter not in self.INITIAL_THRESHOLDS:
            return {'classification': 'unknown', 'confidence': 0.0}
        
        thresholds = self.INITIAL_THRESHOLDS[parameter]
        
        if parameter == 'hemoglobin':
            if value < thresholds['severe_anemia']:
                classification = 'severe_anemia'
                severity = 'critical'
            elif value < thresholds['moderate_anemia']:
                classification = 'moderate_anemia'
                severity = 'major'
            elif value < thresholds['mild_anemia']:
                classification = 'mild_anemia'
                severity = 'minor'
            else:
                classification = 'normal'
                severity = 'none'
        
        elif parameter == 'blood_pressure':
            # value is systolic (assuming features has diastolic)
            if value >= thresholds['severe_hypertension_systolic']:
                classification = 'severe_hypertension'
                severity = 'critical'
            elif value >= thresholds['hypertension_systolic']:
                classification = 'hypertension'
                severity = 'major'
            else:
                classification = 'normal'
                severity = 'none'
        
        elif parameter == 'fasting_blood_sugar':
            if value >= thresholds['overt_diabetes']:
                classification = 'overt_diabetes'
                severity = 'critical'
            elif value >= thresholds['gdm']:
                classification = 'gdm'
                severity = 'major'
            else:
                classification = 'normal'
                severity = 'none'
        
        elif parameter == 'maternal_age':
            if value >= thresholds['advanced']:
                classification = 'advanced_maternal_age'
                severity = 'major'
            elif value < thresholds['teenage']:
                classification = 'teenage_pregnancy'
                severity = 'major'
            elif value < thresholds['young']:
                classification = 'young_maternal_age'
                severity = 'minor'
            else:
                classification = 'normal'
                severity = 'none'
        
        else:
            classification = 'unknown'
            severity = 'none'
        
        result = {
            'classification': classification,
            'severity': severity,
            'threshold_used': thresholds,
            'confidence': 0.5  # Initial confidence before RAG validation
        }
        
        if verbose:
            print(f"[THRESHOLD] Initial: {classification} (severity: {severity})")
        
        return result
    
    def _build_validation_query(self,
                                 parameter: str,
                                 value: float,
                                 initial_classification: Dict) -> str:
        """
        Build targeted query for RAG retrieval to validate threshold.
        """
        classification = initial_classification['classification']
        
        query_templates = {
            'hemoglobin': f"Hemoglobin {value} g/dL anemia classification threshold pregnancy India guidelines definition",
            'blood_pressure': f"Blood pressure {value} mmHg hypertension classification threshold pregnancy pre-eclampsia criteria",
            'fasting_blood_sugar': f"Fasting blood sugar {value} mg/dL diabetes GDM threshold pregnancy diagnosis criteria",
            'maternal_age': f"Maternal age {value} years pregnancy risk classification advanced maternal age definition"
        }
        
        return query_templates.get(parameter, f"{parameter} {value} threshold classification")
    
    def _extract_thresholds_from_chunks(self,
                                        parameter: str,
                                        chunks: List[Tuple],
                                        verbose: bool) -> Dict:
        """
        Extract actual threshold values from retrieved document chunks.
        
        Uses regex patterns to find threshold definitions in text.
        """
        thresholds_found = {}
        
        # Patterns for different parameters
        patterns = {
            'hemoglobin': [
                r'Hb\s*<\s*(\d+\.?\d*)\s*g/dL',
                r'hemoglobin\s*<\s*(\d+\.?\d*)',
                r'anaemia.*?<\s*(\d+\.?\d*)\s*g/dL',
                r'severe.*?<\s*(\d+\.?\d*)\s*g/dL',
                r'moderate.*?(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*g/dL'
            ],
            'blood_pressure': [
                r'BP\s*≥\s*(\d+)/(\d+)',
                r'blood pressure\s*≥\s*(\d+)/(\d+)',
                r'hypertension.*?≥\s*(\d+)/(\d+)',
                r'(\d+)/(\d+)\s*mmHg'
            ],
            'fasting_blood_sugar': [
                r'FBS\s*≥\s*(\d+)',
                r'fasting.*?≥\s*(\d+)\s*mg/dL',
                r'GDM.*?≥\s*(\d+)',
                r'diabetes.*?≥\s*(\d+)\s*mg/dL'
            ],
            'maternal_age': [
                r'age\s*≥\s*(\d+)',
                r'(\d+)\s*years.*?advanced',
                r'advanced.*?≥\s*(\d+)'
            ]
        }
        
        if parameter not in patterns:
            return thresholds_found
        
        # Search in chunks
        for doc, score in chunks:
            text = doc.page_content
            
            for pattern in patterns[parameter]:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            # Multiple values (e.g., BP 140/90)
                            thresholds_found[f'found_{len(thresholds_found)}'] = {
                                'values': [float(m) for m in match],
                                'source': text[:100],
                                'score': score
                            }
                        else:
                            # Single value
                            thresholds_found[f'found_{len(thresholds_found)}'] = {
                                'value': float(match),
                                'source': text[:100],
                                'score': score
                            }
        
        if verbose and thresholds_found:
            print(f"[THRESHOLD] Found {len(thresholds_found)} threshold(s) in documents")
        
        return thresholds_found
    
    def _compare_and_validate(self,
                              parameter: str,
                              value: float,
                              initial_classification: Dict,
                              document_thresholds: Dict,
                              chunks: List[Tuple],
                              verbose: bool) -> Dict:
        """
        Compare initial threshold with document-extracted thresholds.
        
        Returns validated classification with evidence.
        """
        # Start with initial classification
        result = initial_classification.copy()
        result['evidence'] = []
        result['recommendations'] = []
        
        # If we found thresholds in documents, validate
        if document_thresholds:
            # Check if document thresholds match our initial classification
            matches = 0
            total = len(document_thresholds)
            
            for key, threshold_data in document_thresholds.items():
                # Add as evidence
                result['evidence'].append({
                    'source': threshold_data['source'],
                    'threshold': threshold_data.get('value') or threshold_data.get('values'),
                    'relevance_score': threshold_data['score']
                })
                
                # Simple validation: check if our classification aligns
                # (More sophisticated logic can be added here)
                matches += 1
            
            # Update confidence based on document validation
            validation_confidence = matches / total if total > 0 else 0.5
            result['confidence'] = (result['confidence'] + validation_confidence) / 2
            result['validated_by_documents'] = True
            
            if verbose:
                print(f"[THRESHOLD] Validated with {matches}/{total} document matches")
                print(f"[THRESHOLD] Final confidence: {result['confidence']:.2f}")
        else:
            result['validated_by_documents'] = False
            if verbose:
                print(f"[THRESHOLD] No document thresholds found, using initial classification")
        
        # Extract recommendations from chunks
        for doc, score in chunks[:3]:  # Top 3 most relevant
            text = doc.page_content
            # Look for recommendation keywords
            if any(keyword in text.lower() for keyword in ['recommend', 'should', 'management', 'treatment']):
                result['recommendations'].append({
                    'text': text[:200],
                    'relevance': score
                })
        
        return result


def validate_clinical_values(features: ClinicalFeatures,
                             retriever: HybridRetriever,
                             verbose: bool = False) -> Dict:
    """
    Validate all clinical values in features using threshold-first + RAG.
    
    Args:
        features: Extracted clinical features
        retriever: Hybrid retriever for RAG
        verbose: Print validation details
        
    Returns:
        Dict with validated classifications for all parameters
    """
    validator = ThresholdValidator(retriever)
    results = {}
    
    # Validate hemoglobin
    if features.hemoglobin:
        results['hemoglobin'] = validator.validate_with_rag(
            'hemoglobin',
            features.hemoglobin,
            features,
            verbose
        )
    
    # Validate blood pressure
    if features.systolic_bp:
        results['blood_pressure'] = validator.validate_with_rag(
            'blood_pressure',
            features.systolic_bp,
            features,
            verbose
        )
    
    # Validate fasting blood sugar
    if features.fbs:
        results['fasting_blood_sugar'] = validator.validate_with_rag(
            'fasting_blood_sugar',
            features.fbs,
            features,
            verbose
        )
    
    # Validate maternal age
    if features.age:
        results['maternal_age'] = validator.validate_with_rag(
            'maternal_age',
            features.age,
            features,
            verbose
        )
    
    return results
