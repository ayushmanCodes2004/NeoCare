# ============================================================
# clinical_risk_scorer.py — Rule-based clinical risk scoring
# ============================================================
"""
LAYER 2: Clinical Risk Scoring Engine
Applies evidence-based rules to score pregnancy risk before LLM generation.
Prevents retrieval bias and ensures clinical prioritization.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from clinical_preprocessor import ClinicalFeatures


@dataclass
class RiskAssessment:
    """Clinical risk assessment result."""
    risk_level: str  # "low", "moderate", "high", "critical"
    total_score: int
    risk_factors: List[Dict[str, any]]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'risk_level': self.risk_level,
            'total_score': self.total_score,
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
        }


class ClinicalRiskScorer:
    """
    Evidence-based risk scoring for high-risk pregnancy detection.
    
    Scoring is based on established clinical guidelines:
    - Advanced maternal age (≥35): Major risk factor
    - Hypertension/Pre-eclampsia: Major risk factor
    - Gestational diabetes: Major risk factor
    - Severe anemia (Hb <7): Major risk factor
    - Multiple gestation: Major risk factor
    - Previous cesarean: Moderate risk factor
    - Placenta previa: Major risk factor
    """
    
    # Risk scoring weights (evidence-based)
    RISK_SCORES = {
        # Age-related risks
        'advanced_maternal_age': 3,  # Age ≥35
        'teenage_pregnancy': 2,       # Age <18
        
        # Hypertensive disorders
        'hypertensive': 3,            # BP ≥140/90
        'severe_hypertension': 4,     # BP ≥160/110
        
        # Anemia
        'severe_anemia': 3,           # Hb <7
        'moderate_anemia': 2,         # Hb 7-10
        'mild_anemia': 1,             # Hb 10-11
        
        # Glucose disorders
        'diabetic': 3,                # Overt diabetes
        'gestational_diabetes': 3,    # GDM
        'prediabetic': 1,
        
        # Obstetric history
        'previous_cesarean': 2,
        'twin_pregnancy': 3,
        'placenta_previa': 4,
        
        # Other conditions
        'hypothyroidism': 1,
        'iugr': 2,
        'preterm_labor': 2,
    }
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        'low': (0, 1),
        'moderate': (2, 4),
        'high': (5, 7),
        'critical': (8, 100),
    }
    
    def score_risk(self, features: ClinicalFeatures, 
                   additional_conditions: List[str] = None) -> RiskAssessment:
        """
        Calculate clinical risk score based on extracted features.
        
        Args:
            features: ClinicalFeatures from preprocessor
            additional_conditions: List of additional condition keywords detected
            
        Returns:
            RiskAssessment with score, level, and recommendations
        """
        risk_factors = []
        total_score = 0
        
        # Age-based risk
        if features.age_risk_category == "advanced_maternal_age":
            score = self.RISK_SCORES['advanced_maternal_age']
            total_score += score
            risk_factors.append({
                'factor': 'Advanced Maternal Age',
                'value': f'{features.age} years',
                'score': score,
                'severity': 'major',
                'rationale': 'Age ≥35 increases risk of chromosomal abnormalities, GDM, hypertension'
            })
        elif features.age_risk_category == "teenage_pregnancy":
            score = self.RISK_SCORES['teenage_pregnancy']
            total_score += score
            risk_factors.append({
                'factor': 'Teenage Pregnancy',
                'value': f'{features.age} years',
                'score': score,
                'severity': 'moderate',
                'rationale': 'Age <18 increases risk of preterm birth, low birth weight'
            })
        
        # Blood pressure risk
        if features.bp_risk == "hypertensive":
            if features.systolic_bp >= 160 or features.diastolic_bp >= 110:
                score = self.RISK_SCORES['severe_hypertension']
                severity = 'critical'
                rationale = 'Severe hypertension (≥160/110) - risk of eclampsia, stroke, placental abruption'
            else:
                score = self.RISK_SCORES['hypertensive']
                severity = 'major'
                rationale = 'Hypertension (≥140/90) - risk of pre-eclampsia, IUGR, preterm delivery'
            
            total_score += score
            risk_factors.append({
                'factor': 'Hypertension',
                'value': f'{features.systolic_bp}/{features.diastolic_bp} mmHg',
                'score': score,
                'severity': severity,
                'rationale': rationale
            })
        
        # Anemia risk (ONLY if Hb is actually low)
        if features.anemia_risk and "anemia" in features.anemia_risk:
            if features.anemia_risk == "severe_anemia":
                score = self.RISK_SCORES['severe_anemia']
                severity = 'major'
                rationale = 'Severe anemia (Hb <7) - risk of cardiac failure, maternal mortality'
            elif features.anemia_risk == "moderate_anemia":
                score = self.RISK_SCORES['moderate_anemia']
                severity = 'moderate'
                rationale = 'Moderate anemia (Hb 7-10) - increased risk of preterm birth, low birth weight'
            else:  # mild_anemia
                score = self.RISK_SCORES['mild_anemia']
                severity = 'minor'
                rationale = 'Mild anemia (Hb 10-11) - requires iron supplementation'
            
            total_score += score
            risk_factors.append({
                'factor': 'Anemia',
                'value': f'Hb {features.hemoglobin} g/dL',
                'score': score,
                'severity': severity,
                'rationale': rationale
            })
        
        # Glucose risk
        if features.glucose_risk:
            if features.glucose_risk == "diabetic":
                score = self.RISK_SCORES['diabetic']
                severity = 'major'
                rationale = 'Overt diabetes - risk of congenital anomalies, macrosomia, stillbirth'
            elif features.glucose_risk == "gestational_diabetes":
                score = self.RISK_SCORES['gestational_diabetes']
                severity = 'major'
                rationale = 'Gestational diabetes - risk of macrosomia, neonatal hypoglycemia, cesarean'
            elif features.glucose_risk == "prediabetic":
                score = self.RISK_SCORES['prediabetic']
                severity = 'minor'
                rationale = 'Prediabetic glucose levels - requires monitoring and lifestyle modification'
            
            if features.glucose_risk != "normal_glucose":
                total_score += score
                glucose_value = features.fasting_glucose or features.ogtt_glucose or features.random_glucose
                risk_factors.append({
                    'factor': 'Glucose Disorder',
                    'value': f'{glucose_value} mg/dL',
                    'score': score,
                    'severity': severity,
                    'rationale': rationale
                })
        
        # Obstetric history factors
        if features.twin_pregnancy:
            score = self.RISK_SCORES['twin_pregnancy']
            total_score += score
            risk_factors.append({
                'factor': 'Multiple Gestation',
                'value': 'Twin pregnancy',
                'score': score,
                'severity': 'major',
                'rationale': 'Twins increase risk of preterm birth, IUGR, pre-eclampsia'
            })
        
        if features.previous_cesarean:
            score = self.RISK_SCORES['previous_cesarean']
            total_score += score
            risk_factors.append({
                'factor': 'Previous Cesarean Section',
                'value': 'History of LSCS',
                'score': score,
                'severity': 'moderate',
                'rationale': 'Risk of uterine rupture, placenta previa, abnormal placentation'
            })
        
        if features.placenta_previa:
            score = self.RISK_SCORES['placenta_previa']
            total_score += score
            risk_factors.append({
                'factor': 'Placenta Previa',
                'value': 'Low-lying placenta',
                'score': score,
                'severity': 'critical',
                'rationale': 'Risk of severe antepartum hemorrhage, requires cesarean delivery'
            })
        
        # Additional conditions from retrieval/keywords
        if additional_conditions:
            for condition in additional_conditions:
                condition_lower = condition.lower()
                if 'hypothyroid' in condition_lower and not any(rf['factor'] == 'Hypothyroidism' for rf in risk_factors):
                    score = self.RISK_SCORES.get('hypothyroidism', 1)
                    total_score += score
                    risk_factors.append({
                        'factor': 'Hypothyroidism',
                        'value': 'Detected in query/document',
                        'score': score,
                        'severity': 'minor',
                        'rationale': 'Requires levothyroxine supplementation'
                    })
                elif 'iugr' in condition_lower or 'growth retard' in condition_lower:
                    score = self.RISK_SCORES.get('iugr', 2)
                    total_score += score
                    risk_factors.append({
                        'factor': 'IUGR',
                        'value': 'Intrauterine growth restriction',
                        'score': score,
                        'severity': 'moderate',
                        'rationale': 'Risk of stillbirth, requires close monitoring'
                    })
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, risk_factors)
        
        return RiskAssessment(
            risk_level=risk_level,
            total_score=total_score,
            risk_factors=risk_factors,
            recommendations=recommendations
        )
    
    def _determine_risk_level(self, score: int) -> str:
        """Map total score to risk level."""
        for level, (min_score, max_score) in self.RISK_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return level
        return 'high'  # Default to high if score exceeds thresholds
    
    def _generate_recommendations(self, risk_level: str, 
                                   risk_factors: List[Dict]) -> List[str]:
        """Generate clinical recommendations based on risk assessment."""
        recommendations = []
        
        if risk_level == "low":
            recommendations.append("Continue routine antenatal care")
            recommendations.append("Regular ANC visits as per schedule")
        
        elif risk_level == "moderate":
            recommendations.append("Enhanced antenatal surveillance required")
            recommendations.append("More frequent ANC visits recommended")
            recommendations.append("Monitor for development of complications")
        
        elif risk_level in ["high", "critical"]:
            recommendations.append("HIGH-RISK PREGNANCY - Specialist referral required")
            recommendations.append("Delivery at tertiary care facility recommended")
            recommendations.append("Close monitoring with frequent ANC visits")
        
        # Factor-specific recommendations
        for rf in risk_factors:
            factor = rf['factor']
            if factor == 'Advanced Maternal Age':
                recommendations.append("Consider genetic counseling and screening")
            elif factor == 'Hypertension':
                recommendations.append("Monitor BP regularly, consider antihypertensive therapy")
                recommendations.append("Watch for signs of pre-eclampsia (proteinuria, headache, visual changes)")
            elif factor == 'Anemia':
                if rf['severity'] == 'major':
                    recommendations.append("Urgent treatment required - consider blood transfusion")
                else:
                    recommendations.append("Iron and folic acid supplementation")
            elif factor == 'Glucose Disorder':
                recommendations.append("Glucose monitoring, medical nutrition therapy, consider insulin")
            elif factor == 'Placenta Previa':
                recommendations.append("Avoid vaginal examination, plan for cesarean delivery")
                recommendations.append("Watch for painless vaginal bleeding")
        
        return recommendations
    
    def format_risk_summary(self, assessment: RiskAssessment) -> str:
        """Format risk assessment as human-readable text."""
        lines = []
        lines.append(f"RISK LEVEL: {assessment.risk_level.upper()}")
        lines.append(f"Total Risk Score: {assessment.total_score}")
        lines.append("")
        
        if assessment.risk_factors:
            lines.append("Identified Risk Factors:")
            for rf in assessment.risk_factors:
                lines.append(f"  • {rf['factor']}: {rf['value']} (Score: {rf['score']}, Severity: {rf['severity']})")
                lines.append(f"    Rationale: {rf['rationale']}")
        else:
            lines.append("No significant risk factors identified")
        
        lines.append("")
        lines.append("Clinical Recommendations:")
        for rec in assessment.recommendations:
            lines.append(f"  • {rec}")
        
        return "\n".join(lines)
