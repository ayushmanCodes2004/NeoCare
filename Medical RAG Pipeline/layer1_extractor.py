# ============================================================
# layer1_extractor.py — Clinical Feature Extraction (Deterministic)
# ============================================================
"""
LAYER 1: Clinical Feature Extraction

Implements:
- Regex + LLM hybrid extraction
- Unit normalization
- Missing field handling
- Deterministic output with confidence scoring
"""

import re
import requests
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from config_production import OLLAMA_BASE_URL, OLLAMA_MODEL


@dataclass
class ClinicalFeatures:
    """Structured clinical features with confidence scores."""
    # Demographics
    age: Optional[int] = None
    gestational_age_weeks: Optional[int] = None
    
    # Vitals
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    hemoglobin: Optional[float] = None
    fbs: Optional[float] = None  # Fasting blood sugar
    rbs: Optional[float] = None  # Random blood sugar
    ogtt: Optional[float] = None  # Oral glucose tolerance test
    ogtt_2hr_pg: Optional[float] = None  # OGTT 2-hour plasma glucose
    
    # Anthropometric (V2)
    height: Optional[float] = None  # Height in cm
    weight: Optional[float] = None  # Weight in kg
    bmi: Optional[float] = None  # BMI in kg/m²
    
    # Lifestyle (V2)
    smoking: bool = False
    tobacco_use: bool = False
    alcohol_use: bool = False
    
    # Obstetric history
    gravida: Optional[int] = None
    para: Optional[int] = None
    prior_cesarean: bool = False
    twin_pregnancy: bool = False
    placenta_previa: bool = False
    
    # Obstetric history (V2)
    birth_order: Optional[int] = None  # Same as para
    inter_pregnancy_interval: Optional[int] = None  # Months between pregnancies
    stillbirth_count: int = 0
    abortion_count: int = 0
    preterm_history: bool = False
    
    # Serology (V2)
    rh_negative: bool = False
    hiv_positive: bool = False
    syphilis_positive: bool = False
    
    # Pregnancy complications (V2)
    malpresentation: bool = False
    systemic_illness: bool = False
    proteinuria: bool = False
    seizures: bool = False
    
    # Comorbidities
    comorbidities: list = field(default_factory=list)
    
    # Confidence scores per field
    field_confidence: Dict[str, float] = field(default_factory=dict)
    
    # Overall extraction confidence
    extraction_confidence: float = 0.0
    
    # Missing fields
    missing_fields: list = field(default_factory=list)


class ClinicalFeatureExtractor:
    """
    Hybrid extractor using regex (primary) + LLM (fallback).
    Ensures deterministic output with confidence scoring.
    """
    
    # Regex patterns for deterministic extraction
    PATTERNS = {
        'age': [
            r'(\d{1,2})\s*[-\s]?year[-\s]?old',
            r'age\s*(?:of\s*)?(\d{1,2})',
            r'(\d{1,2})\s*(?:year|yr|y)[\s-]*old',
        ],
        'gestational_age': [
            r'(\d{1,2})\s*(?:week|wk|w)s?\s+(?:pregnant|gestation)',
            r'(?:gestational\s+age|GA)\s*(?:of\s*)?(\d{1,2})',
            r'at\s+(\d{1,2})\s*(?:week|wk|w)s?',  # "at 20 weeks"
        ],
        'bp': [
            r'(?:BP|blood\s+pressure)\s*(?:of\s*)?(\d{2,3})\s*/\s*(\d{2,3})',
            r'(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mmHg|mm\s*Hg)',
        ],
        'hemoglobin': [
            r'(?:Hb|hemoglobin|haemoglobin)\s*(?:of\s*)?(\d{1,2}\.?\d*)',
            r'(\d{1,2}\.?\d*)\s*(?:g/dL|gm/dl|g\s*/\s*dL)',
        ],
        'fbs': [
            r'(?:FBS|fasting\s+(?:blood\s+)?(?:sugar|glucose))\s*(?:of\s*)?(\d{2,3})',
        ],
        'rbs': [
            r'(?:RBS|random\s+(?:blood\s+)?(?:sugar|glucose))\s*(?:of\s*)?(\d{2,3})',
        ],
        'ogtt': [
            r'(?:OGTT|oral\s+glucose\s+tolerance)\s*(?:of\s*)?(\d{2,3})',
            r'(?:2\s*hr|2\s*hour)\s+(?:PG|plasma\s+glucose)\s*(?:of\s*)?(\d{2,3})',
        ],
        # V2: Anthropometric
        'height': [
            r'height\s*(?:of\s*)?(\d{2,3})\s*(?:cm|centimeter)',
            r'(\d{2,3})\s*cm\s+(?:tall|height)',
        ],
        'weight': [
            r'weight\s*(?:of\s*)?(\d{2,3})\s*(?:kg|kilogram)',
            r'(\d{2,3})\s*kg\s+weight',
        ],
        'bmi': [
            r'BMI\s*(?:of\s*)?(\d{1,2}\.?\d*)',
            r'body\s+mass\s+index\s*(?:of\s*)?(\d{1,2}\.?\d*)',
        ],
        # V2: Obstetric history
        'birth_order': [
            r'birth\s+order\s*(?:of\s*)?(\d{1,2})',
            r'(?:para|P)\s*(\d{1,2})',
            r'G\d+P(\d+)',  # G3P2 format
        ],
        'inter_pregnancy_interval': [
            r'(?:previous|last)\s+pregnancy\s+(\d{1,3})\s+months?\s+ago',
            r'inter[- ]?pregnancy\s+interval\s*(?:of\s*)?(\d{1,3})\s+months?',
            r'birth\s+spacing\s*(?:of\s*)?(\d{1,3})\s+months?',
        ],
        'stillbirth_count': [
            r'(\d+)\s+stillbirths?',
            r'history\s+of\s+(\d+)\s+stillbirths?',
        ],
        'abortion_count': [
            r'(\d+)\s+abortions?',
            r'history\s+of\s+(\d+)\s+abortions?',
        ],
    }
    
    # Boolean flags
    BOOLEAN_FLAGS = {
        'twin_pregnancy': ['twin', 'twins', 'multiple pregnancy', 'multiple gestation'],
        'prior_cesarean': ['previous c-section', 'previous cesarean', 'previous caesarean', 
                          'prior cesarean', 'LSCS', 'previous CS'],
        'placenta_previa': ['placenta previa', 'placenta praevia', 'low lying placenta'],
        # V2: Lifestyle
        'smoking': ['smoker', 'smoking', 'smokes cigarettes', 'tobacco smoking'],
        'tobacco_use': ['tobacco', 'chewing tobacco', 'gutka', 'paan'],
        'alcohol_use': ['alcohol', 'drinks alcohol', 'alcoholic'],
        # V2: Obstetric history
        'preterm_history': ['previous preterm', 'history of preterm', 'prior preterm delivery'],
        # V2: Serology
        'rh_negative': ['rh negative', 'rh-negative', 'rh -ve', 'rhesus negative'],
        'hiv_positive': ['hiv positive', 'hiv+', 'hiv infected'],
        'syphilis_positive': ['syphilis positive', 'syphilis+', 'vdrl positive'],
        # V2: Complications
        'malpresentation': ['malpresentation', 'breech', 'transverse lie', 'oblique lie'],
        'systemic_illness': ['systemic illness', 'chronic disease', 'medical condition'],
        'proteinuria': ['proteinuria', 'protein in urine', 'urine protein positive'],
        'seizures': ['seizures', 'convulsions', 'fits'],
    }
    
    # Comorbidity keywords
    COMORBIDITY_KEYWORDS = [
        'diabetes', 'hypertension', 'hypothyroid', 'asthma', 'cardiac', 
        'renal', 'hepatic', 'epilepsy', 'syphilis', 'hiv'
    ]
    
    # Negation patterns (TC1-A: Negation Awareness)
    NEGATION_PATTERNS = [
        r'no\s+history\s+of\s+([\w\s,]+?)(?:\.|,|$)',
        r'no\s+known\s+([\w\s,]+?)(?:\.|,|$)',
        r'denies\s+([\w\s,]+?)(?:\.|,|$)',
        r'without\s+([\w\s,]+?)(?:\.|,|$)',
        r'no\s+([\w\s,]+?)\s+history',
    ]
    
    def __init__(self):
        """Initialize extractor."""
        self.llm_available = self._check_llm_availability()
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM is available for fallback extraction."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def extract(self, query: str, verbose: bool = False) -> ClinicalFeatures:
        """
        Extract clinical features from free text query.
        
        Args:
            query: User query (free text)
            verbose: Print extraction details
            
        Returns:
            ClinicalFeatures with confidence scores
        """
        features = ClinicalFeatures()
        query_lower = query.lower()
        
        if verbose:
            print("\n[EXTRACTOR] Starting feature extraction...")
        
        # Extract age
        age, conf = self._extract_age(query_lower)
        if age:
            features.age = age
            features.field_confidence['age'] = conf
        else:
            features.missing_fields.append('age')
        
        # Extract gestational age
        ga, conf = self._extract_gestational_age(query_lower)
        if ga:
            features.gestational_age_weeks = ga
            features.field_confidence['gestational_age'] = conf
        else:
            features.missing_fields.append('gestational_age')
        
        # Extract blood pressure
        bp, conf = self._extract_blood_pressure(query_lower)
        if bp:
            features.systolic_bp, features.diastolic_bp = bp
            features.field_confidence['blood_pressure'] = conf
        else:
            features.missing_fields.append('blood_pressure')
        
        # Extract hemoglobin
        hb, conf = self._extract_hemoglobin(query_lower)
        if hb:
            features.hemoglobin = hb
            features.field_confidence['hemoglobin'] = conf
        else:
            features.missing_fields.append('hemoglobin')
        
        # Extract glucose values
        fbs, conf_fbs = self._extract_glucose(query_lower, 'fbs')
        if fbs:
            features.fbs = fbs
            features.field_confidence['fbs'] = conf_fbs
        
        rbs, conf_rbs = self._extract_glucose(query_lower, 'rbs')
        if rbs:
            features.rbs = rbs
            features.field_confidence['rbs'] = conf_rbs
        
        ogtt, conf_ogtt = self._extract_glucose(query_lower, 'ogtt')
        if ogtt:
            features.ogtt = ogtt
            features.ogtt_2hr_pg = ogtt  # Map to ogtt_2hr_pg for rule engine
            features.field_confidence['ogtt'] = conf_ogtt
        
        if not any([fbs, rbs, ogtt]):
            features.missing_fields.append('glucose')
        
        # V2: Extract anthropometric values
        height, conf_height = self._extract_numeric(query_lower, 'height')
        if height:
            features.height = height
            features.field_confidence['height'] = conf_height
        
        weight, conf_weight = self._extract_numeric(query_lower, 'weight')
        if weight:
            features.weight = weight
            features.field_confidence['weight'] = conf_weight
        
        bmi, conf_bmi = self._extract_numeric(query_lower, 'bmi')
        if bmi:
            features.bmi = bmi
            features.field_confidence['bmi'] = conf_bmi
        elif height and weight:
            # Calculate BMI if both height and weight available
            features.bmi = weight / ((height / 100) ** 2)
            features.field_confidence['bmi'] = min(conf_height, conf_weight)
        
        # V2: Extract obstetric history
        birth_order, conf_birth = self._extract_numeric(query_lower, 'birth_order')
        if birth_order:
            features.birth_order = int(birth_order)
            features.field_confidence['birth_order'] = conf_birth
        elif features.para:
            # Use para as birth_order if not explicitly mentioned
            features.birth_order = features.para
            features.field_confidence['birth_order'] = 0.8
        
        interval, conf_interval = self._extract_numeric(query_lower, 'inter_pregnancy_interval')
        if interval:
            features.inter_pregnancy_interval = int(interval)
            features.field_confidence['inter_pregnancy_interval'] = conf_interval
        
        stillbirth, conf_stillbirth = self._extract_numeric(query_lower, 'stillbirth_count')
        if stillbirth:
            features.stillbirth_count = int(stillbirth)
            features.field_confidence['stillbirth_count'] = conf_stillbirth
        elif 'history of stillbirth' in query_lower or 'previous stillbirth' in query_lower:
            # Singular form without number = 1
            features.stillbirth_count = 1
            features.field_confidence['stillbirth_count'] = 0.9
        
        abortion, conf_abortion = self._extract_numeric(query_lower, 'abortion_count')
        if abortion:
            features.abortion_count = int(abortion)
            features.field_confidence['abortion_count'] = conf_abortion
        elif 'history of abortion' in query_lower or 'previous abortion' in query_lower:
            # Singular form without number = 1
            features.abortion_count = 1
            features.field_confidence['abortion_count'] = 0.9
        
        # Extract boolean flags
        for flag, keywords in self.BOOLEAN_FLAGS.items():
            if any(kw in query_lower for kw in keywords):
                setattr(features, flag, True)
                features.field_confidence[flag] = 1.0
        
        # Extract comorbidities
        features.comorbidities = self._extract_comorbidities(query_lower)
        if features.comorbidities:
            features.field_confidence['comorbidities'] = 0.9
        
        # Calculate overall extraction confidence
        features.extraction_confidence = self._calculate_extraction_confidence(features)
        
        if verbose:
            print(f"[EXTRACTOR] Extraction confidence: {features.extraction_confidence:.2f}")
            print(f"[EXTRACTOR] Missing fields: {features.missing_fields}")
        
        return features
    
    def _extract_age(self, query: str) -> Tuple[Optional[int], float]:
        """Extract age with confidence score."""
        for pattern in self.PATTERNS['age']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 10 <= age <= 60:  # Sanity check
                    return age, 1.0  # High confidence (regex)
        return None, 0.0
    
    def _extract_gestational_age(self, query: str) -> Tuple[Optional[int], float]:
        """Extract gestational age with confidence score."""
        for pattern in self.PATTERNS['gestational_age']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                weeks = int(match.group(1))
                if 1 <= weeks <= 42:  # Sanity check
                    return weeks, 1.0
        return None, 0.0
    
    def _extract_blood_pressure(self, query: str) -> Tuple[Optional[Tuple[int, int]], float]:
        """Extract BP with unit normalization."""
        for pattern in self.PATTERNS['bp']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                systolic = int(match.group(1))
                diastolic = int(match.group(2))
                # Sanity check
                if 70 <= systolic <= 250 and 40 <= diastolic <= 150:
                    return (systolic, diastolic), 1.0
        return None, 0.0
    
    def _extract_hemoglobin(self, query: str) -> Tuple[Optional[float], float]:
        """Extract hemoglobin with unit normalization."""
        for pattern in self.PATTERNS['hemoglobin']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                hb = float(match.group(1))
                # Sanity check
                if 3.0 <= hb <= 20.0:
                    return hb, 1.0
        return None, 0.0
    
    def _extract_glucose(self, query: str, glucose_type: str) -> Tuple[Optional[float], float]:
        """Extract glucose values with unit normalization."""
        patterns = self.PATTERNS.get(glucose_type, [])
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                # Sanity check
                if 30 <= value <= 500:
                    return value, 1.0
        return None, 0.0
    
    def _extract_numeric(self, query: str, field_type: str) -> Tuple[Optional[float], float]:
        """Extract numeric values with unit normalization (V2 generic method)."""
        patterns = self.PATTERNS.get(field_type, [])
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                
                # Sanity checks based on field type
                if field_type == 'height' and 50 <= value <= 250:
                    return value, 1.0
                elif field_type == 'weight' and 20 <= value <= 200:
                    return value, 1.0
                elif field_type == 'bmi' and 10 <= value <= 60:
                    return value, 1.0
                elif field_type == 'birth_order' and 1 <= value <= 20:
                    return value, 1.0
                elif field_type == 'inter_pregnancy_interval' and 1 <= value <= 300:
                    return value, 1.0
                elif field_type in ['stillbirth_count', 'abortion_count'] and 0 <= value <= 20:
                    return value, 1.0
        return None, 0.0
    
    def _extract_comorbidities(self, query: str) -> list:
        """
        Extract comorbidities from query with negation awareness (TC1-A).
        
        CRITICAL: Only extract if EXPLICITLY mentioned in query.
        No hallucinations allowed.
        """
        # First, detect negated terms
        negated_terms = set()
        for pattern in self.NEGATION_PATTERNS:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                # Extract individual conditions from the match
                conditions = [c.strip() for c in match.split(',')]
                negated_terms.update(conditions)
        
        # Convert negated terms to lowercase for matching
        negated_lower = ' '.join(negated_terms).lower()
        
        # Extract comorbidities, excluding negated ones
        found = []
        for keyword in self.COMORBIDITY_KEYWORDS:
            # Check if keyword is in query
            if keyword in query:
                # Check if it's in negated context
                if keyword not in negated_lower:
                    found.append(keyword)
        
        return found
    
    def validate_against_evidence(self, features: ClinicalFeatures, query: str, retrieved_chunks: list) -> ClinicalFeatures:
        """
        Evidence-gated validation: Remove any extracted features not supported by query OR evidence.
        
        CRITICAL SAFETY: Prevents hallucinated conditions.
        
        Args:
            features: Extracted features
            query: Original query
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            Validated features (hallucinations removed)
        """
        query_lower = query.lower()
        
        # Combine all evidence text
        evidence_text = " ".join([
            chunk.page_content.lower() if hasattr(chunk, 'page_content') else str(chunk).lower()
            for chunk in retrieved_chunks
        ])
        
        # Validate comorbidities (most common hallucination source)
        validated_comorbidities = []
        for condition in features.comorbidities:
            # Condition must be in query OR evidence
            if condition in query_lower or condition in evidence_text:
                validated_comorbidities.append(condition)
        
        features.comorbidities = validated_comorbidities
        
        # Validate boolean flags (if not in query, must be in evidence)
        for flag in ['twin_pregnancy', 'prior_cesarean', 'placenta_previa']:
            if getattr(features, flag):
                # Check if mentioned in query
                flag_keywords = self.BOOLEAN_FLAGS[flag]
                in_query = any(kw in query_lower for kw in flag_keywords)
                
                if not in_query:
                    # Must be in evidence
                    in_evidence = any(kw in evidence_text for kw in flag_keywords)
                    if not in_evidence:
                        # Not supported - remove
                        setattr(features, flag, False)
                        if flag in features.field_confidence:
                            del features.field_confidence[flag]
        
        return features
    
    def _calculate_extraction_confidence(self, features: ClinicalFeatures) -> float:
        """
        Calculate overall extraction confidence.
        
        Formula: Average of field confidences
        """
        if not features.field_confidence:
            return 0.0
        
        return sum(features.field_confidence.values()) / len(features.field_confidence)
    
    def to_dict(self, features: ClinicalFeatures) -> Dict:
        """Convert features to dictionary for serialization."""
        return {
            'age': features.age,
            'gestational_age_weeks': features.gestational_age_weeks,
            'systolic_bp': features.systolic_bp,
            'diastolic_bp': features.diastolic_bp,
            'hemoglobin': features.hemoglobin,
            'fbs': features.fbs,
            'rbs': features.rbs,
            'ogtt': features.ogtt,
            'ogtt_2hr_pg': features.ogtt_2hr_pg,
            'gravida': features.gravida,
            'para': features.para,
            'prior_cesarean': features.prior_cesarean,
            'twin_pregnancy': features.twin_pregnancy,
            'placenta_previa': features.placenta_previa,
            # V2: Anthropometric
            'height': features.height,
            'weight': features.weight,
            'bmi': features.bmi,
            # V2: Lifestyle
            'smoking': features.smoking,
            'tobacco_use': features.tobacco_use,
            'alcohol_use': features.alcohol_use,
            # V2: Obstetric history
            'birth_order': features.birth_order,
            'inter_pregnancy_interval': features.inter_pregnancy_interval,
            'stillbirth_count': features.stillbirth_count,
            'abortion_count': features.abortion_count,
            'preterm_history': features.preterm_history,
            # V2: Serology
            'rh_negative': features.rh_negative,
            'hiv_positive': features.hiv_positive,
            'syphilis_positive': features.syphilis_positive,
            # V2: Complications
            'malpresentation': features.malpresentation,
            'systemic_illness': features.systemic_illness,
            'proteinuria': features.proteinuria,
            'seizures': features.seizures,
            # Common
            'comorbidities': features.comorbidities,
            'extraction_confidence': features.extraction_confidence,
            'missing_fields': features.missing_fields,
        }
