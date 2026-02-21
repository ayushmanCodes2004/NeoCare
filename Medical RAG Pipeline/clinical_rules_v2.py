# ============================================================
# clinical_rules_v2.py — Comprehensive HPR Deterministic Engine
# ============================================================
"""
Complete implementation of PMSMA + JOGH + Extended PMSMA thresholds.
Source: COMPLETE_HPR_THRESHOLDS.md

This engine evaluates ALL 19 threshold categories before RAG retrieval.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ============================================================
# 1. ANAEMIA THRESHOLDS
# ============================================================

ANAEMIA_DEFINITION_THRESHOLD = 11.0  # Hb < 11 g/dL in pregnancy

ANAEMIA_THRESHOLDS = {
    "normal":   {"hb_min": 11.0, "hb_max": None,  "label": "No Anaemia",      "score": 0, "severity": "none"},
    "mild":     {"hb_min": 10.0, "hb_max": 10.9,  "label": "Mild Anaemia",    "score": 1, "severity": "minor"},
    "moderate": {"hb_min": 7.0,  "hb_max": 9.9,   "label": "Moderate Anaemia","score": 2, "severity": "moderate"},
    "severe":   {"hb_min": None, "hb_max": 7.0,   "label": "Severe Anaemia",  "score": 4, "severity": "critical"},
}

ANAEMIA_HIGH_RISK_FLAG = 7.0  # Only severe anaemia is HPR
ANAEMIA_REFERRAL_THRESHOLD = 7.0


# ============================================================
# 2. HYPERTENSION THRESHOLDS
# ============================================================

HYPERTENSION_SYSTOLIC_THRESHOLD = 140
HYPERTENSION_DIASTOLIC_THRESHOLD = 90
CHRONIC_HYPERTENSION_GA_THRESHOLD = 20  # Before 20 weeks = chronic

HYPERTENSION_TYPES = {
    "chronic_hypertension": {
        "gestational_age_weeks_max": 20,
        "bp_systolic_min": 140,
        "bp_diastolic_min": 90,
        "score": 3,
        "severity": "major"
    },
    "pregnancy_induced_hypertension": {
        "gestational_age_weeks_min": 20,
        "bp_systolic_min": 140,
        "bp_diastolic_min": 90,
        "proteinuria_required": False,
        "score": 3,
        "severity": "major"
    },
    "pre_eclampsia": {
        "bp_systolic_min": 140,
        "bp_systolic_max": 159,
        "bp_diastolic_min": 90,
        "bp_diastolic_max": 109,
        "proteinuria_required": True,
        "score": 3,
        "severity": "major"
    },
    "severe_pre_eclampsia": {
        "bp_systolic_min": 160,
        "bp_diastolic_min": 110,
        "proteinuria_min": "3+",
        "score": 4,
        "severity": "critical"
    },
    "eclampsia": {
        "bp_systolic_min": 140,
        "bp_diastolic_min": 90,
        "seizures": True,
        "score": 5,
        "severity": "critical"
    }
}


# ============================================================
# 3. GDM THRESHOLDS
# ============================================================

GDM_TEST = {
    "test_type": "75g oral glucose — 2hr Plasma Glucose value",
    "positive_threshold_2hr_pg": 140,  # >= 140 mg/dL = GDM
}

GDM_MANAGEMENT_THRESHOLDS = {
    "mnt_only": {"pppg_threshold": 120, "score": 2, "severity": "moderate"},
    "insulin_therapy": {"pppg_threshold": 120, "score": 2, "severity": "moderate"}
}


# ============================================================
# 4. TSH / THYROID THRESHOLDS
# ============================================================

TSH_NORMAL_RANGES = {
    "trimester_1": {"min": 0.1, "max": 2.5, "unit": "mIU/L"},
    "trimester_2": {"min": 0.2, "max": 3.0, "unit": "mIU/L"},
    "trimester_3": {"min": 0.3, "max": 3.0, "unit": "mIU/L"},
}

HYPOTHYROID_DIAGNOSIS = {
    "subclinical": {"tsh_min": 2.5, "tsh_max": 10.0, "score": 1, "severity": "minor"},
    "overt": {"tsh_min": 10.0, "score": 2, "severity": "moderate"}
}


# ============================================================
# 5. AGE THRESHOLDS
# ============================================================

AGE_RISK_THRESHOLDS = {
    "young_primi": {"age_max": 20, "label": "Young Primi", "score": 3, "severity": "major"},
    "normal_age": {"age_min": 20, "age_max": 35, "label": "Normal Maternal Age", "score": 0, "severity": "none"},
    "advanced_maternal_age": {"age_min": 35, "label": "Elderly Gravida", "score": 3, "severity": "major"}
}


# ============================================================
# 6. ANTHROPOMETRIC THRESHOLDS (NEW)
# ============================================================

SHORT_STATURE_THRESHOLD = 140  # Height < 140 cm
HIGH_BMI_THRESHOLD = 30.0  # BMI >= 30 kg/m²
ASIAN_BMI_THRESHOLD = 25.0  # Asian Indian cutoff
LOW_PRE_PREGNANCY_WEIGHT = 50  # < 50 kg


# ============================================================
# 7. LIFESTYLE RISK THRESHOLDS (NEW)
# ============================================================

LIFESTYLE_RISKS = {
    "smoking": {"score": 2, "severity": "moderate"},
    "tobacco_use": {"score": 2, "severity": "moderate"},
    "alcohol_use": {"score": 2, "severity": "moderate"}
}


# ============================================================
# 8. OBSTETRIC HISTORY THRESHOLDS (NEW)
# ============================================================

HIGH_BIRTH_ORDER_THRESHOLD = 5  # >= 5
SHORT_BIRTH_SPACING_MONTHS = 18  # < 18 months
LONG_BIRTH_SPACING_MONTHS = 59  # > 59 months

OBSTETRIC_HISTORY_SCORES = {
    "high_birth_order": {"score": 2, "severity": "moderate"},
    "short_birth_spacing": {"score": 2, "severity": "moderate"},
    "long_birth_spacing": {"score": 1, "severity": "minor"},
    "previous_preterm": {"score": 2, "severity": "moderate"},
    "previous_stillbirth": {"score": 2, "severity": "moderate"},
    "previous_abortion": {"score": 2, "severity": "moderate"},
    "previous_cs": {"score": 2, "severity": "moderate"}
}


# ============================================================
# 9. BLOOD GROUP / SEROLOGY THRESHOLDS (NEW)
# ============================================================

SEROLOGY_SCORES = {
    "rh_negative": {"score": 1, "severity": "minor"},
    "hiv_positive": {"score": 3, "severity": "major"},
    "syphilis_positive": {"score": 3, "severity": "major"}
}


# ============================================================
# 10. OTHER CONDITIONS
# ============================================================

TWIN_PREGNANCY = {"risk_score": 3, "severity": "major"}
PLACENTA_PREVIA = {"risk_score": 4, "severity": "critical"}
MALPRESENTATION = {"risk_score": 2, "severity": "moderate"}
SYSTEMIC_ILLNESS = {"risk_score": 2, "severity": "moderate"}


# ============================================================
# 11. IUGR THRESHOLDS
# ============================================================

IUGR_THRESHOLDS = {
    "sfh_threshold": {"formula": "SFH_cm < (gestational_age_weeks - 3)", "valid_after_weeks": 20, "score": 3, "severity": "major"},
    "weight_gain": {"threshold_grams_per_week": 500, "score": 3, "severity": "major"}
}


# ============================================================
# 12. COMPREHENSIVE RISK SCORING MATRIX
# ============================================================

RISK_SCORE_MATRIX = {
    # Anaemia
    "severe_anaemia": (4, "critical", "Hb < 7 g/dL"),
    "moderate_anaemia": (2, "moderate", "Hb 7–9.9 g/dL"),
    "mild_anaemia": (1, "minor", "Hb 10–10.9 g/dL"),
    
    # Hypertension
    "severe_pre_eclampsia": (4, "critical", "BP ≥160/110 + proteinuria 3+/4+"),
    "pre_eclampsia": (3, "major", "BP ≥140/90 + proteinuria"),
    "hypertension": (3, "major", "BP ≥140/90"),
    "eclampsia": (5, "critical", "Seizures + BP ≥140/90"),
    
    # GDM
    "gdm_confirmed": (2, "moderate", "2hr PG ≥140 mg/dL"),
    "gdm_screening_pending": (1, "minor", "No OGTT done, GA 14-28 weeks"),
    
    # Thyroid
    "hypothyroid_overt": (2, "moderate", "TSH >10 or TSH >2.5 with low FT4"),
    "hypothyroid_subclinical": (1, "minor", "TSH 2.5–10, normal FT4"),
    
    # Age
    "young_primi": (3, "major", "Age < 20 years"),
    "advanced_maternal_age": (3, "major", "Age > 35 years"),
    
    # Anthropometric (NEW)
    "short_stature": (2, "moderate", "Height < 140 cm"),
    "high_bmi": (2, "moderate", "BMI ≥ 30 kg/m²"),
    
    # Lifestyle (NEW)
    "smoking": (2, "moderate", "Current smoker"),
    "tobacco_use": (2, "moderate", "Tobacco use"),
    "alcohol_use": (2, "moderate", "Alcohol consumption"),
    
    # Obstetric History (NEW)
    "high_birth_order": (2, "moderate", "Birth order ≥ 5"),
    "short_birth_spacing": (2, "moderate", "Inter-pregnancy interval < 18 months"),
    "long_birth_spacing": (1, "minor", "Inter-pregnancy interval > 59 months"),
    "previous_preterm": (2, "moderate", "History of preterm delivery"),
    "previous_stillbirth": (2, "moderate", "History of stillbirth"),
    "previous_abortion": (2, "moderate", "History of abortion"),
    "previous_cs": (2, "moderate", "History of LSCS"),
    
    # Serology (NEW)
    "rh_negative": (1, "minor", "Rh negative blood group"),
    "hiv_positive": (3, "major", "HIV positive"),
    "syphilis_positive": (3, "major", "Syphilis positive"),
    
    # Other Conditions
    "twin_pregnancy": (3, "major", "Multiple gestation"),
    "placenta_previa": (4, "critical", "Confirmed or suspected"),
    "iugr_suspected": (3, "major", "SFH < GA-3 cm"),
    "malpresentation": (2, "moderate", "Abnormal fetal presentation"),
    "systemic_illness": (2, "moderate", "Current or past systemic illness"),
}

RISK_LEVELS = {
    "LOW": {"score_min": 0, "score_max": 2},
    "MODERATE": {"score_min": 3, "score_max": 5},
    "HIGH": {"score_min": 6, "score_max": 8},
    "CRITICAL": {"score_min": 9, "score_max": None}
}


# ============================================================
# 13. BORDERLINE MONITORING THRESHOLDS (NEW)
# ============================================================

BORDERLINE_THRESHOLDS = {
    "borderline_anaemia": {"hb_min": 10.0, "hb_max": 10.9, "action": "IFA twice daily"},
    "pre_hypertension": {"systolic_min": 130, "systolic_max": 139, "diastolic_min": 85, "diastolic_max": 89, "action": "Monitor BP at each visit"},
    "tsh_borderline_t1": {"tsh_min": 2.0, "tsh_max": 2.5, "action": "Repeat TSH in 4 weeks"},
    "tsh_borderline_t2_t3": {"tsh_min": 2.5, "tsh_max": 3.0, "action": "Repeat TSH in 4 weeks"},
}


# ============================================================
# RULE ENGINE RESULT DATACLASS
# ============================================================

@dataclass
class RuleEngineResult:
    """Result from comprehensive HPR rule engine."""
    confirmed_conditions: List[str]
    suspected_conditions: List[str]
    risk_score: int
    risk_level: str
    triggered_rules: List[str]
    risk_flags: List[Dict]
    referral_facility: str
    immediate_referral: bool
    diagnosis_notes: List[str]
    rule_coverage: float = 1.0
    borderline_flags: List[Dict] = None  # NEW: For monitoring
    is_hpr: bool = False  # NEW: Composite HPR flag



# ============================================================
# EVALUATION FUNCTIONS
# ============================================================

def _evaluate_anaemia(hb: float, verbose: bool) -> Optional[Dict]:
    """Evaluate anaemia based on Hb level."""
    if hb >= ANAEMIA_DEFINITION_THRESHOLD:
        return None
    
    # Determine severity
    if hb < ANAEMIA_THRESHOLDS["severe"]["hb_max"]:
        category = "severe"
        condition = "severe_anaemia"
    elif hb < ANAEMIA_THRESHOLDS["moderate"]["hb_max"]:
        category = "moderate"
        condition = "moderate_anaemia"
    else:
        category = "mild"
        condition = "mild_anaemia"
    
    threshold_data = ANAEMIA_THRESHOLDS[category]
    
    if verbose:
        print(f"[RULE] Anaemia: Hb {hb} g/dL -> {threshold_data['label']}")
    
    return {
        "condition": condition,
        "rule": condition,
        "score": threshold_data["score"],
        "flag": {
            "condition": threshold_data["label"],
            "present": True,
            "severity": threshold_data["severity"],
            "value": f"Hb {hb} g/dL",
            "threshold": f"< {ANAEMIA_DEFINITION_THRESHOLD} g/dL",
            "score": threshold_data["score"]
        }
    }


def _evaluate_hypertension(systolic: int, diastolic: int, ga_weeks: Optional[int],
                          proteinuria: bool, seizures: bool, verbose: bool) -> Optional[Dict]:
    """Evaluate hypertension and related conditions."""
    if systolic < HYPERTENSION_SYSTOLIC_THRESHOLD and diastolic < HYPERTENSION_DIASTOLIC_THRESHOLD:
        return None
    
    # Determine type based on GA and symptoms
    if seizures and proteinuria:
        condition = "eclampsia"
        hyp_type = HYPERTENSION_TYPES["eclampsia"]
    elif systolic >= 160 or diastolic >= 110:
        if proteinuria:
            condition = "severe_pre_eclampsia"
            hyp_type = HYPERTENSION_TYPES["severe_pre_eclampsia"]
        else:
            condition = "hypertension"
            hyp_type = HYPERTENSION_TYPES["pregnancy_induced_hypertension"]
    elif proteinuria:
        condition = "pre_eclampsia"
        hyp_type = HYPERTENSION_TYPES["pre_eclampsia"]
    elif ga_weeks and ga_weeks < CHRONIC_HYPERTENSION_GA_THRESHOLD:
        condition = "chronic_hypertension"
        hyp_type = HYPERTENSION_TYPES["chronic_hypertension"]
    else:
        condition = "hypertension"
        hyp_type = HYPERTENSION_TYPES["pregnancy_induced_hypertension"]
    
    if verbose:
        print(f"[RULE] Hypertension: BP {systolic}/{diastolic} -> {condition}")
    
    return {
        "condition": condition,
        "rule": condition,
        "score": hyp_type["score"],
        "confirmed": proteinuria if "eclampsia" in condition else True,
        "flag": {
            "condition": condition.replace("_", " ").title(),
            "present": True,
            "severity": hyp_type["severity"],
            "value": f"BP {systolic}/{diastolic} mmHg",
            "threshold": f">= {HYPERTENSION_SYSTOLIC_THRESHOLD}/{HYPERTENSION_DIASTOLIC_THRESHOLD} mmHg",
            "score": hyp_type["score"]
        }
    }


def _evaluate_gdm(fbs: Optional[float], ogtt_2hr_pg: Optional[float], verbose: bool) -> Optional[Dict]:
    """Evaluate GDM based on OGTT."""
    if ogtt_2hr_pg and ogtt_2hr_pg >= GDM_TEST["positive_threshold_2hr_pg"]:
        if verbose:
            print(f"[RULE] GDM: OGTT 2hr PG {ogtt_2hr_pg} mg/dL -> Confirmed")
        
        return {
            "condition": "gdm_confirmed",
            "rule": "gdm_confirmed",
            "score": 2,
            "confirmed": True,
            "flag": {
                "condition": "GDM Confirmed",
                "present": True,
                "severity": "moderate",
                "value": f"2hr PG {ogtt_2hr_pg} mg/dL",
                "threshold": f">= {GDM_TEST['positive_threshold_2hr_pg']} mg/dL",
                "score": 2
            }
        }
    
    return None


def _evaluate_age(age: int, verbose: bool) -> Optional[Dict]:
    """Evaluate age-related risk."""
    if age < AGE_RISK_THRESHOLDS["young_primi"]["age_max"]:
        category = "young_primi"
        label = "Young Primi"
    elif age >= AGE_RISK_THRESHOLDS["advanced_maternal_age"]["age_min"]:
        category = "advanced_maternal_age"
        label = "Elderly Gravida"
    else:
        return None
    
    threshold_data = AGE_RISK_THRESHOLDS[category]
    
    if verbose:
        print(f"[RULE] Age: {age} years -> {label}")
    
    return {
        "condition": category,
        "rule": category,
        "score": threshold_data["score"],
        "flag": {
            "condition": label,
            "present": True,
            "severity": threshold_data["severity"],
            "value": f"{age} years",
            "score": threshold_data["score"]
        }
    }


def _evaluate_anthropometric(height: Optional[float], bmi: Optional[float], verbose: bool) -> List[Dict]:
    """Evaluate height and BMI risk factors (NEW)."""
    results = []
    
    # Short stature
    if height and height < SHORT_STATURE_THRESHOLD:
        if verbose:
            print(f"[RULE] Short Stature: Height {height} cm -> HPR")
        results.append({
            "condition": "short_stature",
            "rule": "short_stature",
            "score": 2,
            "flag": {
                "condition": "Short Stature",
                "present": True,
                "severity": "moderate",
                "value": f"{height} cm",
                "threshold": f"< {SHORT_STATURE_THRESHOLD} cm",
                "score": 2
            }
        })
    
    # High BMI
    if bmi and bmi >= HIGH_BMI_THRESHOLD:
        if verbose:
            print(f"[RULE] High BMI: {bmi} kg/m² -> HPR")
        results.append({
            "condition": "high_bmi",
            "rule": "high_bmi",
            "score": 2,
            "flag": {
                "condition": "High BMI",
                "present": True,
                "severity": "moderate",
                "value": f"{bmi} kg/m²",
                "threshold": f">= {HIGH_BMI_THRESHOLD} kg/m²",
                "score": 2
            }
        })
    
    return results


def _evaluate_lifestyle(smoking: bool, tobacco: bool, alcohol: bool, verbose: bool) -> List[Dict]:
    """Evaluate lifestyle risk factors (NEW)."""
    results = []
    
    if smoking:
        if verbose:
            print(f"[RULE] Smoking: Current smoker -> HPR")
        results.append({
            "condition": "smoking",
            "rule": "smoking",
            "score": 2,
            "flag": {
                "condition": "Smoking",
                "present": True,
                "severity": "moderate",
                "value": "Current smoker",
                "score": 2
            }
        })
    
    if tobacco:
        if verbose:
            print(f"[RULE] Tobacco Use: Active -> HPR")
        results.append({
            "condition": "tobacco_use",
            "rule": "tobacco_use",
            "score": 2,
            "flag": {
                "condition": "Tobacco Use",
                "present": True,
                "severity": "moderate",
                "value": "Tobacco user",
                "score": 2
            }
        })
    
    if alcohol:
        if verbose:
            print(f"[RULE] Alcohol Use: Active -> HPR")
        results.append({
            "condition": "alcohol_use",
            "rule": "alcohol_use",
            "score": 2,
            "flag": {
                "condition": "Alcohol Use",
                "present": True,
                "severity": "moderate",
                "value": "Alcohol consumer",
                "score": 2
            }
        })
    
    return results


def _evaluate_obstetric_history(birth_order: Optional[int], inter_pregnancy_interval: Optional[int],
                                stillbirth_count: int, abortion_count: int, preterm_history: bool,
                                verbose: bool) -> List[Dict]:
    """Evaluate obstetric history risk factors (NEW)."""
    results = []
    
    # High birth order
    if birth_order and birth_order >= HIGH_BIRTH_ORDER_THRESHOLD:
        if verbose:
            print(f"[RULE] High Birth Order: {birth_order} -> HPR")
        results.append({
            "condition": "high_birth_order",
            "rule": "high_birth_order",
            "score": 2,
            "flag": {
                "condition": "High Birth Order",
                "present": True,
                "severity": "moderate",
                "value": f"Birth order {birth_order}",
                "threshold": f">= {HIGH_BIRTH_ORDER_THRESHOLD}",
                "score": 2
            }
        })
    
    # Birth spacing
    if inter_pregnancy_interval is not None:
        if inter_pregnancy_interval < SHORT_BIRTH_SPACING_MONTHS:
            if verbose:
                print(f"[RULE] Short Birth Spacing: {inter_pregnancy_interval} months -> HPR")
            results.append({
                "condition": "short_birth_spacing",
                "rule": "short_birth_spacing",
                "score": 2,
                "flag": {
                    "condition": "Short Birth Spacing",
                    "present": True,
                    "severity": "moderate",
                    "value": f"{inter_pregnancy_interval} months",
                    "threshold": f"< {SHORT_BIRTH_SPACING_MONTHS} months",
                    "score": 2
                }
            })
        elif inter_pregnancy_interval > LONG_BIRTH_SPACING_MONTHS:
            if verbose:
                print(f"[RULE] Long Birth Spacing: {inter_pregnancy_interval} months -> Monitor")
            results.append({
                "condition": "long_birth_spacing",
                "rule": "long_birth_spacing",
                "score": 1,
                "flag": {
                    "condition": "Long Birth Spacing",
                    "present": True,
                    "severity": "minor",
                    "value": f"{inter_pregnancy_interval} months",
                    "threshold": f"> {LONG_BIRTH_SPACING_MONTHS} months",
                    "score": 1
                }
            })
    
    # Stillbirth history
    if stillbirth_count > 0:
        if verbose:
            print(f"[RULE] Previous Stillbirth: {stillbirth_count} -> HPR")
        results.append({
            "condition": "previous_stillbirth",
            "rule": "previous_stillbirth",
            "score": 2,
            "flag": {
                "condition": "Previous Stillbirth",
                "present": True,
                "severity": "moderate",
                "value": f"{stillbirth_count} stillbirth(s)",
                "score": 2
            }
        })
    
    # Abortion history
    if abortion_count > 0:
        if verbose:
            print(f"[RULE] Previous Abortion: {abortion_count} -> HPR")
        results.append({
            "condition": "previous_abortion",
            "rule": "previous_abortion",
            "score": 2,
            "flag": {
                "condition": "Previous Abortion",
                "present": True,
                "severity": "moderate",
                "value": f"{abortion_count} abortion(s)",
                "score": 2
            }
        })
    
    # Preterm delivery history
    if preterm_history:
        if verbose:
            print(f"[RULE] Previous Preterm Delivery -> HPR")
        results.append({
            "condition": "previous_preterm",
            "rule": "previous_preterm",
            "score": 2,
            "flag": {
                "condition": "Previous Preterm Delivery",
                "present": True,
                "severity": "moderate",
                "value": "History of preterm delivery",
                "score": 2
            }
        })
    
    return results


def _evaluate_serology(rh_negative: bool, hiv_positive: bool, syphilis_positive: bool,
                       verbose: bool) -> List[Dict]:
    """Evaluate blood group and serology risk factors (NEW)."""
    results = []
    
    if rh_negative:
        if verbose:
            print(f"[RULE] Rh Negative -> HPR")
        results.append({
            "condition": "rh_negative",
            "rule": "rh_negative",
            "score": 1,
            "flag": {
                "condition": "Rh Negative",
                "present": True,
                "severity": "minor",
                "value": "Rh negative blood group",
                "score": 1
            }
        })
    
    if hiv_positive:
        if verbose:
            print(f"[RULE] HIV Positive -> HPR")
        results.append({
            "condition": "hiv_positive",
            "rule": "hiv_positive",
            "score": 3,
            "flag": {
                "condition": "HIV Positive",
                "present": True,
                "severity": "major",
                "value": "HIV confirmed",
                "score": 3
            }
        })
    
    if syphilis_positive:
        if verbose:
            print(f"[RULE] Syphilis Positive -> HPR")
        results.append({
            "condition": "syphilis_positive",
            "rule": "syphilis_positive",
            "score": 3,
            "flag": {
                "condition": "Syphilis Positive",
                "present": True,
                "severity": "major",
                "value": "Syphilis confirmed",
                "score": 3
            }
        })
    
    return results



def _calculate_risk_level(total_score: int) -> str:
    """Calculate risk level from total score."""
    for level, thresholds in RISK_LEVELS.items():
        if thresholds["score_max"] is None:
            if total_score >= thresholds["score_min"]:
                return level
        elif thresholds["score_min"] <= total_score <= thresholds["score_max"]:
            return level
    return "LOW"


def _determine_referral(confirmed: List[str], suspected: List[str], risk_level: str) -> Tuple[str, bool]:
    """Determine referral facility and urgency."""
    immediate_conditions = [
        "eclampsia", "severe_pre_eclampsia", "severe_anaemia", "placenta_previa",
        "hiv_positive", "syphilis_positive"
    ]
    
    # Check for immediate referral conditions
    immediate = any(cond in confirmed or cond in suspected for cond in immediate_conditions)
    
    # Determine facility
    if risk_level == "CRITICAL" or immediate:
        facility = "CEmOC/District Hospital"
    elif risk_level == "HIGH":
        facility = "FRU/CHC"
    elif risk_level == "MODERATE":
        facility = "CHC/PHC"
    else:
        facility = "PHC"
    
    return facility, immediate


def _check_borderline_values(features: Dict, verbose: bool) -> List[Dict]:
    """Check for borderline values that need monitoring (NEW)."""
    borderline_flags = []
    
    # Borderline anaemia
    hb = features.get('hemoglobin')
    if hb and 10.0 <= hb < 11.0:
        borderline_flags.append({
            "condition": "Borderline Anaemia",
            "value": f"Hb {hb} g/dL",
            "action": "IFA twice daily, monitor monthly",
            "severity": "watch"
        })
        if verbose:
            print(f"[BORDERLINE] Anaemia: Hb {hb} g/dL (watch)")
    
    # Pre-hypertension
    systolic = features.get('systolic_bp')
    diastolic = features.get('diastolic_bp')
    if systolic and diastolic:
        if (130 <= systolic < 140) or (85 <= diastolic < 90):
            borderline_flags.append({
                "condition": "Pre-Hypertension",
                "value": f"BP {systolic}/{diastolic} mmHg",
                "action": "Monitor BP at each visit",
                "severity": "watch"
            })
            if verbose:
                print(f"[BORDERLINE] BP: {systolic}/{diastolic} mmHg (watch)")
    
    return borderline_flags


def run_rule_engine(features: Dict, verbose: bool = False) -> RuleEngineResult:
    """
    Run comprehensive HPR rule engine BEFORE RAG retrieval.
    
    Args:
        features: Extracted clinical features
        verbose: Print rule evaluation
        
    Returns:
        RuleEngineResult with confirmed/suspected conditions and HPR flag
    """
    confirmed_conditions = []
    suspected_conditions = []
    triggered_rules = []
    risk_flags = []
    diagnosis_notes = []
    total_score = 0
    
    if verbose:
        print("\n[RULE ENGINE] Evaluating comprehensive HPR thresholds...")
    
    # 1. ANAEMIA
    if features.get('hemoglobin'):
        hb = features['hemoglobin']
        anaemia_result = _evaluate_anaemia(hb, verbose)
        if anaemia_result:
            confirmed_conditions.append(anaemia_result['condition'])
            triggered_rules.append(anaemia_result['rule'])
            risk_flags.append(anaemia_result['flag'])
            total_score += anaemia_result['score']
    
    # 2. HYPERTENSION
    if features.get('systolic_bp') and features.get('diastolic_bp'):
        bp_result = _evaluate_hypertension(
            features['systolic_bp'],
            features['diastolic_bp'],
            features.get('gestational_age_weeks'),
            features.get('proteinuria', False),
            features.get('seizures', False),
            verbose
        )
        if bp_result:
            if bp_result.get('confirmed'):
                confirmed_conditions.append(bp_result['condition'])
            else:
                suspected_conditions.append(bp_result['condition'])
                diagnosis_notes.append(bp_result.get('note', ''))
            
            triggered_rules.append(bp_result['rule'])
            risk_flags.append(bp_result['flag'])
            total_score += bp_result['score']
    
    # 3. GDM
    if features.get('fbs') or features.get('ogtt_2hr_pg'):
        gdm_result = _evaluate_gdm(
            features.get('fbs'),
            features.get('ogtt_2hr_pg'),
            verbose
        )
        if gdm_result:
            if gdm_result.get('confirmed'):
                confirmed_conditions.append(gdm_result['condition'])
            else:
                suspected_conditions.append(gdm_result['condition'])
                diagnosis_notes.append(gdm_result.get('note', ''))
            
            triggered_rules.append(gdm_result['rule'])
            risk_flags.append(gdm_result['flag'])
            total_score += gdm_result['score']
    
    # GDM SCREENING CHECK
    ga_weeks = features.get('gestational_age_weeks') or 0
    ogtt_done = features.get('ogtt_2hr_pg') is not None and features.get('ogtt_2hr_pg') > 0
    gdm_confirmed = 'gdm' in confirmed_conditions or 'gdm_confirmed' in triggered_rules
    
    if not gdm_confirmed and not ogtt_done and ga_weeks >= 14:
        if 14 <= ga_weeks < 24:
            suspected_conditions.append("gdm_screening_pending")
            triggered_rules.append("gdm_screening_pending")
            diagnosis_notes.append("GDM First Screening Pending - 75g OGTT required (14-28 weeks)")
            risk_flags.append({
                "condition": "GDM First Screening Pending",
                "present": True,
                "severity": "minor",
                "value": f"GA {ga_weeks} weeks, no OGTT done",
                "threshold": "OGTT required at 14-28 weeks",
                "score": 1
            })
            total_score += 1
            if verbose:
                print(f"[RULE] GDM Screening: Pending (GA {ga_weeks} weeks)")
        elif 24 <= ga_weeks <= 28:
            suspected_conditions.append("gdm_screening_due")
            triggered_rules.append("gdm_screening_due")
            diagnosis_notes.append("GDM Second Screening Due - 75g OGTT required now")
            risk_flags.append({
                "condition": "GDM Second Screening Due",
                "present": True,
                "severity": "minor",
                "value": f"GA {ga_weeks} weeks, no OGTT done",
                "threshold": "OGTT required at 24-28 weeks",
                "score": 1
            })
            total_score += 1
            if verbose:
                print(f"[RULE] GDM Screening: Due (GA {ga_weeks} weeks)")
        elif ga_weeks > 28:
            suspected_conditions.append("gdm_screening_overdue")
            triggered_rules.append("gdm_screening_overdue")
            diagnosis_notes.append("GDM Screening Overdue - 75g OGTT should have been done")
            risk_flags.append({
                "condition": "GDM Screening Overdue",
                "present": True,
                "severity": "minor",
                "value": f"GA {ga_weeks} weeks, no OGTT done",
                "threshold": "OGTT should have been done by 28 weeks",
                "score": 1
            })
            total_score += 1
            if verbose:
                print(f"[RULE] GDM Screening: Overdue (GA {ga_weeks} weeks)")
    
    # 4. AGE
    if features.get('age'):
        age_result = _evaluate_age(features['age'], verbose)
        if age_result:
            confirmed_conditions.append(age_result['condition'])
            triggered_rules.append(age_result['rule'])
            risk_flags.append(age_result['flag'])
            total_score += age_result['score']
    
    # 5. ANTHROPOMETRIC (NEW)
    anthro_results = _evaluate_anthropometric(
        features.get('height'),
        features.get('bmi'),
        verbose
    )
    for result in anthro_results:
        confirmed_conditions.append(result['condition'])
        triggered_rules.append(result['rule'])
        risk_flags.append(result['flag'])
        total_score += result['score']
    
    # 6. LIFESTYLE (NEW)
    lifestyle_results = _evaluate_lifestyle(
        features.get('smoking', False),
        features.get('tobacco_use', False),
        features.get('alcohol_use', False),
        verbose
    )
    for result in lifestyle_results:
        confirmed_conditions.append(result['condition'])
        triggered_rules.append(result['rule'])
        risk_flags.append(result['flag'])
        total_score += result['score']
    
    # 7. OBSTETRIC HISTORY (NEW)
    obstetric_results = _evaluate_obstetric_history(
        features.get('birth_order'),
        features.get('inter_pregnancy_interval'),
        features.get('stillbirth_count', 0),
        features.get('abortion_count', 0),
        features.get('preterm_history', False),
        verbose
    )
    for result in obstetric_results:
        confirmed_conditions.append(result['condition'])
        triggered_rules.append(result['rule'])
        risk_flags.append(result['flag'])
        total_score += result['score']
    
    # 8. SEROLOGY (NEW)
    serology_results = _evaluate_serology(
        features.get('rh_negative', False),
        features.get('hiv_positive', False),
        features.get('syphilis_positive', False),
        verbose
    )
    for result in serology_results:
        confirmed_conditions.append(result['condition'])
        triggered_rules.append(result['rule'])
        risk_flags.append(result['flag'])
        total_score += result['score']
    
    # 9. TWIN PREGNANCY
    if features.get('twin_pregnancy'):
        confirmed_conditions.append("twin_pregnancy")
        triggered_rules.append("twin_pregnancy")
        risk_flags.append({
            "condition": "Twin Pregnancy",
            "present": True,
            "severity": "major",
            "value": "Multiple gestation",
            "score": 3
        })
        total_score += 3
    
    # 10. PREVIOUS CESAREAN
    if features.get('prior_cesarean'):
        confirmed_conditions.append("previous_cs")
        triggered_rules.append("previous_cs")
        risk_flags.append({
            "condition": "Previous Cesarean",
            "present": True,
            "severity": "moderate",
            "value": "History of LSCS",
            "score": 2
        })
        total_score += 2
    
    # 11. PLACENTA PREVIA
    if features.get('placenta_previa'):
        confirmed_conditions.append("placenta_previa")
        triggered_rules.append("placenta_previa")
        risk_flags.append({
            "condition": "Placenta Previa",
            "present": True,
            "severity": "critical",
            "value": "Confirmed or suspected",
            "score": 4
        })
        total_score += 4
    
    # 12. MALPRESENTATION (NEW)
    if features.get('malpresentation'):
        confirmed_conditions.append("malpresentation")
        triggered_rules.append("malpresentation")
        risk_flags.append({
            "condition": "Malpresentation",
            "present": True,
            "severity": "moderate",
            "value": "Abnormal fetal presentation",
            "score": 2
        })
        total_score += 2
    
    # 13. SYSTEMIC ILLNESS (NEW)
    if features.get('systemic_illness'):
        confirmed_conditions.append("systemic_illness")
        triggered_rules.append("systemic_illness")
        risk_flags.append({
            "condition": "Systemic Illness",
            "present": True,
            "severity": "moderate",
            "value": "Current or past systemic illness",
            "score": 2
        })
        total_score += 2
    
    # Calculate risk level
    risk_level = _calculate_risk_level(total_score)
    
    # Determine referral facility
    referral_facility, immediate_referral = _determine_referral(
        confirmed_conditions,
        suspected_conditions,
        risk_level
    )
    
    # Check borderline values
    borderline_flags = _check_borderline_values(features, verbose)
    
    # Determine composite HPR flag (Section 19 logic)
    is_hpr = _determine_hpr_flag(triggered_rules)
    
    if verbose:
        print(f"[RULE ENGINE] Confirmed: {len(confirmed_conditions)} conditions")
        print(f"[RULE ENGINE] Suspected: {len(suspected_conditions)} conditions")
        print(f"[RULE ENGINE] Risk Score: {total_score} ({risk_level})")
        print(f"[RULE ENGINE] IS_HPR: {is_hpr}")
        print(f"[RULE ENGINE] Referral: {referral_facility}")
    
    return RuleEngineResult(
        confirmed_conditions=confirmed_conditions,
        suspected_conditions=suspected_conditions,
        risk_score=total_score,
        risk_level=risk_level,
        triggered_rules=triggered_rules,
        risk_flags=risk_flags,
        referral_facility=referral_facility,
        immediate_referral=immediate_referral,
        diagnosis_notes=diagnosis_notes,
        rule_coverage=1.0,
        borderline_flags=borderline_flags,
        is_hpr=is_hpr
    )


def _determine_hpr_flag(triggered_rules: List[str]) -> bool:
    """
    Determine composite HPR flag based on Section 19 logic.
    
    IS_HPR = TRUE if ANY of the HPR conditions are triggered.
    """
    HPR_CONDITIONS = [
        "severe_anaemia",  # Only severe, not mild/moderate
        "hypertension", "pre_eclampsia", "severe_pre_eclampsia", "eclampsia",
        "gdm_confirmed",  # Only confirmed, not screening
        "hypothyroid_overt", "hypothyroid_subclinical",
        "young_primi", "advanced_maternal_age",
        "short_stature", "high_bmi",
        "smoking", "tobacco_use", "alcohol_use",
        "high_birth_order", "short_birth_spacing",
        "previous_preterm", "previous_stillbirth", "previous_abortion", "previous_cs",
        "rh_negative",
        "hiv_positive", "syphilis_positive",
        "twin_pregnancy", "placenta_previa", "malpresentation",
        "systemic_illness"
    ]
    
    return any(rule in HPR_CONDITIONS for rule in triggered_rules)
