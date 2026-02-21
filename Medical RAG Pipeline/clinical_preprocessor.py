# ============================================================
# clinical_preprocessor.py — Query preprocessing and feature extraction
# ============================================================
"""
LAYER 1: Query Preprocessing
Extracts structured clinical features from free text queries.
Normalizes clinical concepts and rewrites queries for better retrieval.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ClinicalFeatures:
    """Structured clinical features extracted from query."""
    age: Optional[int] = None
    gestational_age_weeks: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    hemoglobin: Optional[float] = None
    fasting_glucose: Optional[float] = None
    random_glucose: Optional[float] = None
    ogtt_glucose: Optional[float] = None
    
    # Boolean flags for key conditions
    twin_pregnancy: bool = False
    previous_cesarean: bool = False
    placenta_previa: bool = False
    diabetes_mentioned: bool = False
    hypertension_mentioned: bool = False
    
    # Normalized risk categories
    age_risk_category: Optional[str] = None  # "advanced_maternal_age", "teenage", "normal"
    anemia_risk: Optional[str] = None  # "severe", "moderate", "mild", "normal"
    bp_risk: Optional[str] = None  # "hypertensive", "normal", "hypotensive"
    glucose_risk: Optional[str] = None  # "diabetic", "prediabetic", "normal"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ClinicalPreprocessor:
    """
    Extracts structured clinical data from free text queries.
    Normalizes medical concepts and rewrites queries for semantic search.
    """
    
    # Age extraction patterns
    AGE_PATTERNS = [
        r'(\d{1,2})\s*[-\s]?year[-\s]?old',
        r'age\s*(?:of\s*)?(\d{1,2})',
        r'(\d{1,2})\s*(?:year|yr|y)[\s-]*old\s+(?:woman|female|patient|pregnant)',
        r'(?:woman|female|patient)\s+(?:of\s+)?(\d{1,2})\s+years',
    ]
    
    # Gestational age patterns
    GA_PATTERNS = [
        r'(\d{1,2})\s*(?:week|wk|w)s?\s+(?:pregnant|gestation)',
        r'(?:gestational\s+age|GA)\s*(?:of\s*)?(\d{1,2})',
        r'(\d{1,2})\s*(?:week|wk|w)s?\s+(?:of\s+)?(?:pregnancy|gestation)',
    ]
    
    # Blood pressure patterns (systolic/diastolic)
    BP_PATTERNS = [
        r'(?:BP|blood\s+pressure)\s*(?:of\s*)?(\d{2,3})\s*/\s*(\d{2,3})',
        r'(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mmHg|mm\s*Hg)?',
    ]
    
    # Hemoglobin patterns
    HB_PATTERNS = [
        r'(?:Hb|hemoglobin|haemoglobin)\s*(?:of\s*)?(\d{1,2}\.?\d*)',
        r'(\d{1,2}\.?\d*)\s*(?:g/dL|gm/dl|g\s*/\s*dL)',
    ]
    
    # Glucose patterns
    GLUCOSE_PATTERNS = {
        'fasting': r'(?:FBS|fasting\s+(?:blood\s+)?(?:sugar|glucose))\s*(?:of\s*)?(\d{2,3})',
        'random': r'(?:RBS|random\s+(?:blood\s+)?(?:sugar|glucose))\s*(?:of\s*)?(\d{2,3})',
        'ogtt': r'(?:OGTT|oral\s+glucose\s+tolerance)\s*(?:of\s*)?(\d{2,3})',
    }
    
    # Keyword flags
    KEYWORD_FLAGS = {
        'twin_pregnancy': ['twin', 'twins', 'multiple pregnancy', 'multiple gestation'],
        'previous_cesarean': ['previous c-section', 'previous cesarean', 'previous caesarean', 
                              'prior cesarean', 'LSCS', 'previous CS'],
        'placenta_previa': ['placenta previa', 'placenta praevia', 'low lying placenta'],
        'diabetes_mentioned': ['diabetes', 'diabetic', 'GDM', 'gestational diabetes'],
        'hypertension_mentioned': ['hypertension', 'high blood pressure', 'high BP', 
                                   'pre-eclampsia', 'preeclampsia', 'PIH'],
    }
    
    def extract_features(self, query: str) -> ClinicalFeatures:
        """
        Extract all structured clinical features from query text.
        
        Args:
            query: Raw user query text
            
        Returns:
            ClinicalFeatures object with extracted and normalized data
        """
        features = ClinicalFeatures()
        query_lower = query.lower()
        
        # Extract age
        features.age = self._extract_age(query_lower)
        if features.age:
            features.age_risk_category = self._categorize_age_risk(features.age)
        
        # Extract gestational age
        features.gestational_age_weeks = self._extract_gestational_age(query_lower)
        
        # Extract blood pressure
        bp_values = self._extract_blood_pressure(query_lower)
        if bp_values:
            features.systolic_bp, features.diastolic_bp = bp_values
            features.bp_risk = self._categorize_bp_risk(features.systolic_bp, features.diastolic_bp)
        
        # Extract hemoglobin
        features.hemoglobin = self._extract_hemoglobin(query_lower)
        if features.hemoglobin:
            features.anemia_risk = self._categorize_anemia_risk(features.hemoglobin)
        
        # Extract glucose values
        glucose_values = self._extract_glucose(query_lower)
        features.fasting_glucose = glucose_values.get('fasting')
        features.random_glucose = glucose_values.get('random')
        features.ogtt_glucose = glucose_values.get('ogtt')
        if any(glucose_values.values()):
            features.glucose_risk = self._categorize_glucose_risk(glucose_values)
        
        # Extract keyword flags
        for flag_name, keywords in self.KEYWORD_FLAGS.items():
            if any(kw in query_lower for kw in keywords):
                setattr(features, flag_name, True)
        
        return features
    
    def _extract_age(self, query: str) -> Optional[int]:
        """Extract age from query text."""
        for pattern in self.AGE_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 10 <= age <= 60:  # Sanity check
                    return age
        return None
    
    def _extract_gestational_age(self, query: str) -> Optional[int]:
        """Extract gestational age in weeks."""
        for pattern in self.GA_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                weeks = int(match.group(1))
                if 1 <= weeks <= 42:  # Sanity check
                    return weeks
        return None
    
    def _extract_blood_pressure(self, query: str) -> Optional[tuple]:
        """Extract systolic and diastolic BP."""
        for pattern in self.BP_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                systolic = int(match.group(1))
                diastolic = int(match.group(2))
                # Sanity check: typical ranges
                if 70 <= systolic <= 250 and 40 <= diastolic <= 150:
                    return (systolic, diastolic)
        return None
    
    def _extract_hemoglobin(self, query: str) -> Optional[float]:
        """Extract hemoglobin value."""
        for pattern in self.HB_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                hb = float(match.group(1))
                if 3.0 <= hb <= 20.0:  # Sanity check
                    return hb
        return None
    
    def _extract_glucose(self, query: str) -> Dict[str, Optional[float]]:
        """Extract glucose values (fasting, random, OGTT)."""
        glucose_values = {'fasting': None, 'random': None, 'ogtt': None}
        for glucose_type, pattern in self.GLUCOSE_PATTERNS.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                if 30 <= value <= 500:  # Sanity check
                    glucose_values[glucose_type] = value
        return glucose_values
    
    def _categorize_age_risk(self, age: int) -> str:
        """Categorize age into risk groups."""
        if age >= 35:
            return "advanced_maternal_age"
        elif age < 18:
            return "teenage_pregnancy"
        else:
            return "normal_age"
    
    def _categorize_anemia_risk(self, hb: float) -> str:
        """
        Categorize anemia risk based on Hb levels.
        WHO criteria for pregnant women: Hb < 11 g/dL = anemia
        """
        if hb < 7.0:
            return "severe_anemia"
        elif hb < 10.0:
            return "moderate_anemia"
        elif hb < 11.0:
            return "mild_anemia"
        else:
            return "normal_hemoglobin"
    
    def _categorize_bp_risk(self, systolic: int, diastolic: int) -> str:
        """Categorize BP risk (hypertension threshold: 140/90)."""
        if systolic >= 140 or diastolic >= 90:
            return "hypertensive"
        elif systolic < 90 or diastolic < 60:
            return "hypotensive"
        else:
            return "normal_bp"
    
    def _categorize_glucose_risk(self, glucose_values: Dict[str, Optional[float]]) -> str:
        """
        Categorize glucose risk based on available values.
        GDM criteria: FBS ≥ 92 mg/dL, OGTT ≥ 140 mg/dL
        """
        fbs = glucose_values.get('fasting')
        ogtt = glucose_values.get('ogtt')
        rbs = glucose_values.get('random')
        
        if (fbs and fbs >= 126) or (ogtt and ogtt >= 200) or (rbs and rbs >= 200):
            return "diabetic"
        elif (fbs and fbs >= 92) or (ogtt and ogtt >= 140):
            return "gestational_diabetes"
        elif (fbs and fbs >= 100) or (rbs and rbs >= 140):
            return "prediabetic"
        else:
            return "normal_glucose"
    
    def rewrite_query(self, query: str, features: ClinicalFeatures) -> str:
        """
        Rewrite query into structured clinical format for better embedding alignment.
        
        NEW FORMAT: Structured Clinical Query with normalized values
        
        Args:
            query: Original query
            features: Extracted clinical features
            
        Returns:
            Structured query optimized for embedding search
        """
        parts = []
        
        # Start with structured clinical summary
        parts.append("Clinical Query:")
        
        # Age information
        if features.age:
            age_status = ""
            if features.age_risk_category == "advanced_maternal_age":
                age_status = " (advanced maternal age, high risk)"
            elif features.age_risk_category == "teenage_pregnancy":
                age_status = " (teenage pregnancy, high risk)"
            else:
                age_status = " (normal age)"
            parts.append(f"Age: {features.age} years{age_status}")
        
        # Gestational age
        if features.gestational_age_weeks:
            parts.append(f"Gestational age: {features.gestational_age_weeks} weeks")
        
        # Blood pressure
        if features.systolic_bp and features.diastolic_bp:
            bp_status = ""
            if features.bp_risk == "hypertensive":
                bp_status = " (hypertension, requires management)"
            elif features.bp_risk == "hypotensive":
                bp_status = " (hypotension)"
            else:
                bp_status = " (normal blood pressure)"
            parts.append(f"BP: {features.systolic_bp}/{features.diastolic_bp} mmHg{bp_status}")
        
        # Hemoglobin
        if features.hemoglobin:
            hb_status = ""
            if features.anemia_risk == "severe_anemia":
                hb_status = " (severe anaemia, urgent treatment needed)"
            elif features.anemia_risk == "moderate_anemia":
                hb_status = " (moderate anaemia)"
            elif features.anemia_risk == "mild_anemia":
                hb_status = " (mild anaemia)"
            else:
                hb_status = " (normal haemoglobin)"
            parts.append(f"Hb: {features.hemoglobin} g/dL{hb_status}")
        
        # Glucose
        if features.fasting_glucose:
            glucose_status = ""
            if features.glucose_risk and "diabet" in features.glucose_risk:
                glucose_status = " (elevated, diabetes concern)"
            else:
                glucose_status = " (normal fasting glucose)"
            parts.append(f"FBS: {features.fasting_glucose} mg/dL{glucose_status}")
        
        # Obstetric history
        if features.twin_pregnancy:
            parts.append("Multiple gestation: twin pregnancy (high risk)")
        if features.previous_cesarean:
            parts.append("Previous caesarean section (requires monitoring)")
        if features.placenta_previa:
            parts.append("Placenta previa (high risk, bleeding concern)")
        
        # Add search intent
        parts.append("Goal: Risk classification and clinical guidance using document thresholds and guidelines")
        
        # Add relevant medical terms for better retrieval
        search_terms = []
        if features.age_risk_category == "advanced_maternal_age":
            search_terms.extend(["advanced maternal age", "elderly gravida", "age-related risks"])
        if features.anemia_risk and "anemia" in features.anemia_risk:
            search_terms.extend(["anaemia in pregnancy", "haemoglobin management", "iron supplementation"])
        if features.bp_risk == "hypertensive":
            search_terms.extend(["hypertension in pregnancy", "pre-eclampsia", "blood pressure management"])
        if features.glucose_risk and "diabet" in features.glucose_risk:
            search_terms.extend(["gestational diabetes", "GDM", "glucose management"])
        
        if search_terms:
            parts.append(f"Relevant topics: {', '.join(search_terms)}")
        
        return " | ".join(parts)
    
    def process_query(self, query: str) -> Dict:
        """
        Full preprocessing pipeline.
        
        Returns:
            Dict with:
                - original_query: str
                - extracted_features: ClinicalFeatures
                - rewritten_query: str
                - feature_dict: dict (JSON-serializable)
        """
        features = self.extract_features(query)
        rewritten = self.rewrite_query(query, features)
        
        return {
            'original_query': query,
            'extracted_features': features,
            'rewritten_query': rewritten,
            'feature_dict': features.to_dict(),
        }
