# ============================================================
# layer3_rules.py — Clinical Rule Engine (Authoritative Layer)
# ============================================================
"""
LAYER 3: Clinical Rule Engine

Hard-coded medical rules that OVERRIDE LLM hallucinations.
Runs BEFORE LLM reasoning.

Rules:
- Age ≥35 → Advanced maternal age → HIGH RISK
- Hb <11 → Anaemia
- BP ≥140/90 → Hypertension → HIGH RISK
- Twin pregnancy → HIGH RISK
"""

from typing import Dict, List
from dataclasses import dataclass, field
from layer1_extractor import ClinicalFeatures
from config_production import CLINICAL_THRESHOLDS


@dataclass
class RiskFlag:
    """Individual risk flag."""
    condition: str
    present: bool
    severity: str  # 'minor', 'moderate', 'major', 'critical'
    value: str
    threshold: str
    rationale: str
    score: int


@dataclass
class RuleEngineOutput:
    """Output from clinical rule engine."""
    risk_flags: List[RiskFlag] = field(default_factory=list)
    overall_risk: str = "LOW"  # LOW, MODERATE, HIGH, CRITICAL
    total_score: int = 0
    rule_coverage: float = 0.0  # % of features with applicable rules
    triggered_rules: List[str] = field(default_factory=list)


class ClinicalRuleEngine:
    """
    Authoritative clinical rule engine.
    Cannot be overridden by LLM.
    """
    
    # Risk scores
    RISK_SCORES = {
        'advanced_maternal_age': 3,
        'young_maternal_age': 1,  # Age < 20 (teen pregnancy risk)
        'teenage_pregnancy': 2,
        'severe_hypertension': 4,
        'hypertension': 3,
        'severe_anemia': 3,
        'moderate_anemia': 2,
        'mild_anemia': 1,
        'diabetes': 3,
        'gdm': 3,
        'twin_pregnancy': 3,
        'prior_cesarean': 2,
        'placenta_previa': 4,
    }
    
    # Risk thresholds
    RISK_LEVELS = {
        'low': (0, 1),
        'moderate': (2, 4),
        'high': (5, 7),
        'critical': (8, 100),
    }
    
    def __init__(self):
        """Initialize rule engine."""
        self.thresholds = CLINICAL_THRESHOLDS
    
    def apply_rules(self, features: ClinicalFeatures, verbose: bool = False) -> RuleEngineOutput:
        """
        Apply hard-coded clinical rules to features.
        
        Args:
            features: Extracted clinical features
            verbose: Print rule triggers
            
        Returns:
            RuleEngineOutput with risk flags
        """
        output = RuleEngineOutput()
        
        if verbose:
            print("\n[RULE ENGINE] Applying clinical rules...")
        
        # Rule 1: Age-based risk
        if features.age is not None:
            if features.age >= self.thresholds['advanced_maternal_age']:
                flag = RiskFlag(
                    condition="Advanced Maternal Age",
                    present=True,
                    severity="major",
                    value=f"{features.age} years",
                    threshold=f"≥{self.thresholds['advanced_maternal_age']} years",
                    rationale="Age ≥35 increases risk of chromosomal abnormalities, GDM, hypertension, cesarean delivery",
                    score=self.RISK_SCORES['advanced_maternal_age']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("advanced_maternal_age")
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: Advanced Maternal Age (Age {features.age} ≥ 35)")
            
            elif features.age < 20:
                # Young maternal age (19-20 = mild risk, <18 = higher risk)
                if features.age < self.thresholds['teenage_pregnancy_max']:
                    flag = RiskFlag(
                        condition="Teenage Pregnancy",
                        present=True,
                        severity="moderate",
                        value=f"{features.age} years",
                        threshold=f"<{self.thresholds['teenage_pregnancy_max']} years",
                        rationale="Age <18 increases risk of preterm birth, low birth weight, maternal complications",
                        score=self.RISK_SCORES['teenage_pregnancy']
                    )
                    output.risk_flags.append(flag)
                    output.total_score += flag.score
                    output.triggered_rules.append("teenage_pregnancy")
                    
                    if verbose:
                        print(f"  ✓ RULE TRIGGERED: Teenage Pregnancy (Age {features.age} < 18)")
                else:
                    # Age 18-19: Young maternal age
                    flag = RiskFlag(
                        condition="Young Maternal Age",
                        present=True,
                        severity="minor",
                        value=f"{features.age} years",
                        threshold="<20 years",
                        rationale="Age <20 associated with increased risk of preterm birth, anemia, and inadequate prenatal care",
                        score=self.RISK_SCORES['young_maternal_age']
                    )
                    output.risk_flags.append(flag)
                    output.total_score += flag.score
                    output.triggered_rules.append("young_maternal_age")
                    
                    if verbose:
                        print(f"  ✓ RULE TRIGGERED: Young Maternal Age (Age {features.age} < 20)")
        
        # Rule 2: Hemoglobin-based risk (Anaemia)
        if features.hemoglobin is not None:
            if features.hemoglobin < self.thresholds['severe_anemia']:
                flag = RiskFlag(
                    condition="Severe Anaemia",
                    present=True,
                    severity="critical",
                    value=f"Hb {features.hemoglobin} g/dL",
                    threshold=f"<{self.thresholds['severe_anemia']} g/dL",
                    rationale="Severe anaemia (Hb <7) - risk of cardiac failure, maternal mortality, urgent treatment required",
                    score=self.RISK_SCORES['severe_anemia']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("severe_anemia")
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: Severe Anaemia (Hb {features.hemoglobin} < 7)")
            
            elif features.hemoglobin < self.thresholds['moderate_anemia']:
                flag = RiskFlag(
                    condition="Moderate Anaemia",
                    present=True,
                    severity="major",
                    value=f"Hb {features.hemoglobin} g/dL",
                    threshold=f"<{self.thresholds['moderate_anemia']} g/dL",
                    rationale="Moderate anaemia (Hb 7-10) - increased risk of preterm birth, low birth weight",
                    score=self.RISK_SCORES['moderate_anemia']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("moderate_anemia")
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: Moderate Anaemia (Hb {features.hemoglobin} 7-10)")
            
            elif features.hemoglobin < self.thresholds['mild_anemia']:
                flag = RiskFlag(
                    condition="Mild Anaemia",
                    present=True,
                    severity="moderate",
                    value=f"Hb {features.hemoglobin} g/dL",
                    threshold=f"<{self.thresholds['mild_anemia']} g/dL",
                    rationale="Mild anaemia (Hb 10-11) - requires iron and folic acid supplementation",
                    score=self.RISK_SCORES['mild_anemia']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("mild_anemia")
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: Mild Anaemia (Hb {features.hemoglobin} 10-11)")
        
        # Rule 3: Blood Pressure-based risk (Hypertension)
        if features.systolic_bp is not None and features.diastolic_bp is not None:
            if (features.systolic_bp >= self.thresholds['severe_hypertension_systolic'] or 
                features.diastolic_bp >= self.thresholds['severe_hypertension_diastolic']):
                flag = RiskFlag(
                    condition="Severe Hypertension",
                    present=True,
                    severity="critical",
                    value=f"BP {features.systolic_bp}/{features.diastolic_bp} mmHg",
                    threshold=f"≥{self.thresholds['severe_hypertension_systolic']}/{self.thresholds['severe_hypertension_diastolic']} mmHg",
                    rationale="Severe hypertension (≥160/110) - risk of eclampsia, stroke, placental abruption, immediate intervention required",
                    score=self.RISK_SCORES['severe_hypertension']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("severe_hypertension")
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: Severe Hypertension (BP {features.systolic_bp}/{features.diastolic_bp} ≥ 160/110)")
            
            elif (features.systolic_bp >= self.thresholds['hypertension_systolic'] or 
                  features.diastolic_bp >= self.thresholds['hypertension_diastolic']):
                flag = RiskFlag(
                    condition="Hypertension",
                    present=True,
                    severity="major",
                    value=f"BP {features.systolic_bp}/{features.diastolic_bp} mmHg",
                    threshold=f"≥{self.thresholds['hypertension_systolic']}/{self.thresholds['hypertension_diastolic']} mmHg",
                    rationale="Hypertension (≥140/90) - risk of pre-eclampsia, IUGR, preterm delivery, requires antihypertensive therapy",
                    score=self.RISK_SCORES['hypertension']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("hypertension")
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: Hypertension (BP {features.systolic_bp}/{features.diastolic_bp} ≥ 140/90)")
        
        # Rule 4: Glucose-based risk (Diabetes/GDM)
        glucose_risk = False
        if features.fbs is not None:
            if features.fbs >= self.thresholds['diabetes_fbs']:
                flag = RiskFlag(
                    condition="Overt Diabetes",
                    present=True,
                    severity="major",
                    value=f"FBS {features.fbs} mg/dL",
                    threshold=f"≥{self.thresholds['diabetes_fbs']} mg/dL",
                    rationale="Overt diabetes (FBS ≥126) - risk of congenital anomalies, macrosomia, stillbirth, requires insulin",
                    score=self.RISK_SCORES['diabetes']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("diabetes")
                glucose_risk = True
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: Overt Diabetes (FBS {features.fbs} ≥ 126)")
            
            elif features.fbs >= self.thresholds['gdm_fbs']:
                flag = RiskFlag(
                    condition="Gestational Diabetes Mellitus (GDM)",
                    present=True,
                    severity="major",
                    value=f"FBS {features.fbs} mg/dL",
                    threshold=f"≥{self.thresholds['gdm_fbs']} mg/dL",
                    rationale="GDM (FBS ≥92) - risk of macrosomia, neonatal hypoglycemia, cesarean delivery, requires medical nutrition therapy",
                    score=self.RISK_SCORES['gdm']
                )
                output.risk_flags.append(flag)
                output.total_score += flag.score
                output.triggered_rules.append("gdm")
                glucose_risk = True
                
                if verbose:
                    print(f"  ✓ RULE TRIGGERED: GDM (FBS {features.fbs} ≥ 92)")
        
        # Rule 5: Twin pregnancy
        if features.twin_pregnancy:
            flag = RiskFlag(
                condition="Multiple Gestation (Twins)",
                present=True,
                severity="major",
                value="Twin pregnancy",
                threshold="N/A",
                rationale="Twin pregnancy increases risk of preterm birth, IUGR, pre-eclampsia, requires enhanced surveillance",
                score=self.RISK_SCORES['twin_pregnancy']
            )
            output.risk_flags.append(flag)
            output.total_score += flag.score
            output.triggered_rules.append("twin_pregnancy")
            
            if verbose:
                print(f"  ✓ RULE TRIGGERED: Twin Pregnancy")
        
        # Rule 6: Prior cesarean
        if features.prior_cesarean:
            flag = RiskFlag(
                condition="Previous Cesarean Section",
                present=True,
                severity="moderate",
                value="History of LSCS",
                threshold="N/A",
                rationale="Previous cesarean increases risk of uterine rupture, placenta previa, abnormal placentation",
                score=self.RISK_SCORES['prior_cesarean']
            )
            output.risk_flags.append(flag)
            output.total_score += flag.score
            output.triggered_rules.append("prior_cesarean")
            
            if verbose:
                print(f"  ✓ RULE TRIGGERED: Previous Cesarean")
        
        # Rule 7: Placenta previa
        if features.placenta_previa:
            flag = RiskFlag(
                condition="Placenta Previa",
                present=True,
                severity="critical",
                value="Low-lying placenta",
                threshold="N/A",
                rationale="Placenta previa - risk of severe antepartum hemorrhage, requires cesarean delivery, close monitoring",
                score=self.RISK_SCORES['placenta_previa']
            )
            output.risk_flags.append(flag)
            output.total_score += flag.score
            output.triggered_rules.append("placenta_previa")
            
            if verbose:
                print(f"  ✓ RULE TRIGGERED: Placenta Previa")
        
        # Determine overall risk level
        output.overall_risk = self._determine_risk_level(output.total_score)
        
        # Calculate rule coverage
        output.rule_coverage = self._calculate_rule_coverage(features, output)
        
        if verbose:
            print(f"\n[RULE ENGINE] Overall Risk: {output.overall_risk}")
            print(f"[RULE ENGINE] Total Score: {output.total_score}")
            print(f"[RULE ENGINE] Rule Coverage: {output.rule_coverage:.2f}")
        
        return output
    
    def _determine_risk_level(self, score: int) -> str:
        """Determine risk level from total score."""
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= score <= max_score:
                return level.upper()
        return "HIGH"
    
    def _calculate_rule_coverage(self, features: ClinicalFeatures, output: RuleEngineOutput) -> float:
        """
        Calculate rule coverage: % of extracted features with applicable rules.
        
        Formula: (features with rules) / (total extracted features)
        """
        total_features = 0
        features_with_rules = 0
        
        # Count extracted features
        if features.age is not None:
            total_features += 1
            if any(r in output.triggered_rules for r in ['advanced_maternal_age', 'young_maternal_age', 'teenage_pregnancy']):
                features_with_rules += 1
        
        if features.hemoglobin is not None:
            total_features += 1
            if any(r in output.triggered_rules for r in ['severe_anemia', 'moderate_anemia', 'mild_anemia']):
                features_with_rules += 1
        
        if features.systolic_bp is not None:
            total_features += 1
            if any(r in output.triggered_rules for r in ['severe_hypertension', 'hypertension']):
                features_with_rules += 1
        
        if features.fbs is not None or features.rbs is not None or features.ogtt is not None:
            total_features += 1
            if any(r in output.triggered_rules for r in ['diabetes', 'gdm']):
                features_with_rules += 1
        
        if features.twin_pregnancy:
            total_features += 1
            features_with_rules += 1
        
        if features.prior_cesarean:
            total_features += 1
            features_with_rules += 1
        
        if features.placenta_previa:
            total_features += 1
            features_with_rules += 1
        
        if total_features == 0:
            return 0.0
        
        return features_with_rules / total_features
