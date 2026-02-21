# ============================================================
# clinical_rules.py — Pre-RAG Clinical Rule Engine
# ============================================================
"""
Hard-coded clinical thresholds from GoI High-Risk Pregnancy Guidelines.
Runs BEFORE RAG retrieval to establish confirmed conditions.

Source: clinical_thresholds.md (from High-Risk-Conditions-in-preg-modified-Final.pdf)

Pipeline Flow:
Input → Rule Engine (this file) → Confirmed Conditions → Chunk Gate → RAG → Output
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ============================================================
# 1. ANAEMIA THRESHOLDS (Page 4)
# ============================================================

ANAEMIA_DEFINITION_THRESHOLD = 11.0  # Hb < 11 g/dL

ANAEMIA_THRESHOLDS = {
    "normal":   {"hb_min": 11.0, "hb_max": None,  "label": "No Anaemia",      "score": 0, "severity": "none"},
    "mild":     {"hb_min": 10.0, "hb_max": 10.9,  "label": "Mild Anaemia",    "score": 1, "severity": "minor"},
    "moderate": {"hb_min": 7.0,  "hb_max": 9.9,   "label": "Moderate Anaemia","score": 2, "severity": "moderate"},
    "severe":   {"hb_min": None, "hb_max": 7.0,   "label": "Severe Anaemia",  "score": 4, "severity": "critical"},
}

ANAEMIA_HIGH_RISK_FLAG = 7.0
ANAEMIA_REFERRAL_THRESHOLD = 7.0


# ============================================================
# 2. HYPERTENSION THRESHOLDS (Page 3)
# ============================================================

HYPERTENSION_SYSTOLIC_THRESHOLD = 140
HYPERTENSION_DIASTOLIC_THRESHOLD = 90

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
# 3. GDM THRESHOLDS (Pages 8-10)
# ============================================================

GDM_TEST = {
    "test_type": "75g oral glucose — 2hr Plasma Glucose value",
    "positive_threshold_2hr_pg": 140,  # 2hr PG >= 140 mg/dL = POSITIVE
}

GDM_MANAGEMENT_THRESHOLDS = {
    "mnt_only": {
        "pppg_threshold": 120,
        "score": 2,
        "severity": "moderate"
    },
    "insulin_therapy": {
        "pppg_threshold": 120,
        "score": 2,
        "severity": "moderate"
    }
}


# ============================================================
# 4. HYPOTHYROIDISM THRESHOLDS (Page 7)
# ============================================================

TSH_NORMAL_RANGES = {
    "trimester_1": {"min": 0.1, "max": 2.5, "unit": "mIU/L"},
    "trimester_2": {"min": 0.2, "max": 3.0, "unit": "mIU/L"},
    "trimester_3": {"min": 0.3, "max": 3.0, "unit": "mIU/L"},
}

HYPOTHYROID_DIAGNOSIS = {
    "subclinical": {
        "tsh_min": 2.5,
        "tsh_max": 10.0,
        "score": 1,
        "severity": "minor"
    },
    "overt": {
        "tsh_min": 10.0,
        "score": 2,
        "severity": "moderate"
    }
}


# ============================================================
# 5. AGE-RELATED RISK (Page 2)
# ============================================================

AGE_RISK_THRESHOLDS = {
    "young_primi": {
        "age_max": 20,
        "label": "Young Primi",
        "score": 3,
        "severity": "major"
    },
    "normal_age": {
        "age_min": 20,
        "age_max": 35,
        "label": "Normal Maternal Age",
        "score": 0,
        "severity": "none"
    },
    "advanced_maternal_age": {
        "age_min": 35,
        "label": "Elderly Gravida",
        "score": 3,
        "severity": "major"
    }
}


# ============================================================
# 6. IUGR THRESHOLDS (Page 12)
# ============================================================

IUGR_THRESHOLDS = {
    "sfh_threshold": {
        "formula": "SFH_cm < (gestational_age_weeks - 3)",
        "valid_after_weeks": 20,
        "score": 3,
        "severity": "major"
    },
    "weight_gain": {
        "threshold_grams_per_week": 500,
        "score": 3,
        "severity": "major"
    }
}


# ============================================================
# 7. OTHER CONDITIONS
# ============================================================

TWIN_PREGNANCY = {
    "risk_score": 3,
    "severity": "major"
}

PLACENTA_PREVIA = {
    "risk_score": 4,
    "severity": "critical"
}

PREVIOUS_CS = {
    "risk_score": 2,
    "severity": "moderate"
}


# ============================================================
# 8. RISK SCORING MATRIX
# ============================================================

RISK_SCORE_MATRIX = {
    "severe_anaemia":              (4, "critical", "Hb < 7 g/dL"),
    "moderate_anaemia":            (2, "moderate", "Hb 7–9.9 g/dL"),
    "mild_anaemia":                (1, "minor",    "Hb 10–10.9 g/dL"),
    "severe_pre_eclampsia":        (4, "critical", "BP ≥160/110 + proteinuria 3+/4+"),
    "pre_eclampsia":               (3, "major",    "BP ≥140/90 + proteinuria"),
    "hypertension":                (3, "major",    "BP ≥140/90"),
    "eclampsia":                   (5, "critical", "Seizures + BP ≥140/90"),
    "gdm":                         (2, "moderate", "2hr PG ≥140 mg/dL"),
    "hypothyroid_overt":           (2, "moderate", "TSH >10 or TSH >2.5 with low FT4"),
    "hypothyroid_subclinical":     (1, "minor",    "TSH 2.5–10, normal FT4"),
    "twin_pregnancy":              (3, "major",    "Multiple gestation"),
    "advanced_maternal_age":       (3, "major",    "Age > 35 years"),
    "young_primi":                 (3, "major",    "Age < 20 years"),
    "previous_cs":                 (2, "moderate", "History of LSCS"),
    "placenta_previa":             (4, "critical", "Confirmed or suspected"),
    "iugr_suspected":              (3, "major",    "SFH < GA-3 cm"),
}

RISK_LEVELS = {
    "LOW":      {"score_min": 0,  "score_max": 2},
    "MODERATE": {"score_min": 3,  "score_max": 5},
    "HIGH":     {"score_min": 6,  "score_max": 8},
    "CRITICAL": {"score_min": 9,  "score_max": None}
}


# ============================================================
# 9. DIAGNOSIS CONFIRMATION REQUIREMENTS
# ============================================================

DIAGNOSIS_CONFIRMATION_REQUIRED = {
    "pre_eclampsia": {
        "required_criteria": ["bp_elevated", "proteinuria_result"],
        "confirmatory_test": "urine dipstick or 24hr urine protein",
        "if_test_unavailable": "SUSPECTED pre-eclampsia — confirm at referral"
    },
    "severe_pre_eclampsia": {
        "required_criteria": ["bp_gte_160_110", "proteinuria_3plus"],
        "confirmatory_test": "urine dipstick",
        "if_test_unavailable": "SUSPECTED severe pre-eclampsia"
    },
    "gdm": {
        "required_criteria": ["ogtt_2hr_pg_gte_140"],
        "confirmatory_test": "75g OGTT — 2hr plasma glucose",
        "if_test_unavailable": "GDM CANNOT be confirmed without OGTT"
    },
    "iugr": {
        "required_criteria": ["sfh_3cm_below_ga OR weight_gain_lt_500g_per_week"],
        "confirmatory": "USG fetal biometry",
        "if_usg_unavailable": "SUSPECTED IUGR — confirm with USG at referral"
    }
}


# ============================================================
# CLINICAL RULE ENGINE
# ============================================================

@dataclass
class RuleEngineResult:
    """Result from clinical rule engine."""
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


def run_rule_engine(features: Dict, verbose: bool = False) -> RuleEngineResult:
    """
    Run clinical rule engine BEFORE RAG retrieval.
    
    Args:
        features: Extracted clinical features
        verbose: Print rule evaluation
        
    Returns:
        RuleEngineResult with confirmed/suspected conditions
    """
    confirmed_conditions = []
    suspected_conditions = []
    triggered_rules = []
    risk_flags = []
    diagnosis_notes = []
    total_score = 0
    
    if verbose:
        print("\n[RULE ENGINE] Evaluating clinical thresholds...")
    
    # 1. ANAEMIA RULES
    if features.get('hemoglobin'):
        hb = features['hemoglobin']
        anaemia_result = _evaluate_anaemia(hb, verbose)
        if anaemia_result:
            confirmed_conditions.append(anaemia_result['condition'])
            triggered_rules.append(anaemia_result['rule'])
            risk_flags.append(anaemia_result['flag'])
            total_score += anaemia_result['score']
    
    # 2. HYPERTENSION RULES
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
    
    # 3. GDM RULES
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
    
    # FIX 4: GDM SCREENING DUE/OVERDUE CHECK
    # Check if GDM screening is needed based on GA and OGTT status
    ga_weeks = features.get('gestational_age_weeks') or 0
    ogtt_done = features.get('ogtt_2hr_pg') is not None and features.get('ogtt_2hr_pg') > 0
    gdm_confirmed = 'gdm' in confirmed_conditions or 'gdm_confirmed' in triggered_rules
    
    if not gdm_confirmed and not ogtt_done and ga_weeks >= 14:
        if 14 <= ga_weeks < 24:
            # First screening window
            suspected_conditions.append("gdm_screening_pending")
            triggered_rules.append("gdm_screening_pending")
            diagnosis_notes.append("GDM First Screening Pending - 75g OGTT required at earliest contact (Page 8)")
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
                print(f"[RULE] GDM Screening: Pending (GA {ga_weeks} weeks, first window)")
        
        elif 24 <= ga_weeks <= 28:
            # Second screening window - due now
            suspected_conditions.append("gdm_screening_due")
            triggered_rules.append("gdm_screening_due")
            diagnosis_notes.append("GDM Second Screening Due - 75g OGTT required, 24-28 week window open now (Page 8)")
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
                print(f"[RULE] GDM Screening: Due (GA {ga_weeks} weeks, second window)")
        
        elif ga_weeks > 28:
            # Overdue - should have been done
            suspected_conditions.append("gdm_screening_overdue")
            triggered_rules.append("gdm_screening_overdue")
            diagnosis_notes.append("GDM Screening Overdue - 75g OGTT not done, perform at this visit immediately (Page 8)")
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
    
    # 4. AGE RULES
    if features.get('age'):
        age_result = _evaluate_age(features['age'], verbose)
        if age_result:
            confirmed_conditions.append(age_result['condition'])
            triggered_rules.append(age_result['rule'])
            risk_flags.append(age_result['flag'])
            total_score += age_result['score']
    
    # 5. TWIN PREGNANCY
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
    
    # 6. PREVIOUS CESAREAN
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
    
    # 7. PLACENTA PREVIA
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
    
    # Calculate risk level
    risk_level = _calculate_risk_level(total_score)
    
    # Determine referral facility
    referral_facility, immediate_referral = _determine_referral(
        confirmed_conditions,
        suspected_conditions,
        risk_level
    )
    
    if verbose:
        print(f"[RULE ENGINE] Confirmed: {len(confirmed_conditions)} conditions")
        print(f"[RULE ENGINE] Suspected: {len(suspected_conditions)} conditions")
        print(f"[RULE ENGINE] Risk Score: {total_score} ({risk_level})")
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
        rule_coverage=1.0
    )


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
        print(f"[RULE] Anaemia: Hb {hb} g/dL → {threshold_data['label']}")
    
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
    # Check if hypertensive
    if systolic < HYPERTENSION_SYSTOLIC_THRESHOLD and diastolic < HYPERTENSION_DIASTOLIC_THRESHOLD:
        return None
    
    # Determine type
    if seizures:
        condition = "eclampsia"
        rule = "eclampsia"
        score = 5
        severity = "critical"
        confirmed = True
        note = None
    elif systolic >= 160 or diastolic >= 110:
        if proteinuria:
            condition = "severe_pre_eclampsia"
            rule = "severe_pre_eclampsia"
            score = 4
            severity = "critical"
            confirmed = True
            note = None
        else:
            condition = "severe_pre_eclampsia"
            rule = "severe_hypertension"
            score = 4
            severity = "critical"
            confirmed = False
            note = "SUSPECTED severe pre-eclampsia — proteinuria status unconfirmed"
    else:
        if proteinuria:
            condition = "pre_eclampsia"
            rule = "pre_eclampsia"
            score = 3
            severity = "major"
            confirmed = True
            note = None
        else:
            condition = "hypertension"
            rule = "hypertension"
            score = 3
            severity = "major"
            confirmed = True
            note = None
    
    if verbose:
        print(f"[RULE] Hypertension: BP {systolic}/{diastolic} → {condition}")
    
    return {
        "condition": condition,
        "rule": rule,
        "score": score,
        "confirmed": confirmed,
        "note": note,
        "flag": {
            "condition": condition.replace("_", " ").title(),
            "present": True,
            "severity": severity,
            "value": f"BP {systolic}/{diastolic} mmHg",
            "threshold": f"≥ {HYPERTENSION_SYSTOLIC_THRESHOLD}/{HYPERTENSION_DIASTOLIC_THRESHOLD} mmHg",
            "score": score
        }
    }


def _evaluate_gdm(fbs: Optional[float], ogtt_2hr_pg: Optional[float], verbose: bool) -> Optional[Dict]:
    """Evaluate GDM based on OGTT (NOT FBS)."""
    # GDM diagnosis requires OGTT 2hr PG >= 140 mg/dL
    if ogtt_2hr_pg and ogtt_2hr_pg >= GDM_TEST["positive_threshold_2hr_pg"]:
        if verbose:
            print(f"[RULE] GDM: OGTT 2hr PG {ogtt_2hr_pg} mg/dL → Confirmed")
        
        return {
            "condition": "gdm",
            "rule": "gdm_confirmed",
            "score": 2,
            "confirmed": True,
            "flag": {
                "condition": "Gestational Diabetes Mellitus (GDM)",
                "present": True,
                "severity": "moderate",
                "value": f"OGTT 2hr PG {ogtt_2hr_pg} mg/dL",
                "threshold": f"≥ {GDM_TEST['positive_threshold_2hr_pg']} mg/dL",
                "score": 2
            }
        }
    elif fbs and fbs >= 92:
        # FBS alone cannot confirm GDM per guidelines
        if verbose:
            print(f"[RULE] GDM: FBS {fbs} mg/dL → Suspected (needs OGTT confirmation)")
        
        return {
            "condition": "gdm",
            "rule": "gdm_suspected",
            "score": 2,
            "confirmed": False,
            "note": "GDM suspected based on FBS — requires OGTT confirmation",
            "flag": {
                "condition": "Gestational Diabetes Mellitus (GDM) - Suspected",
                "present": True,
                "severity": "moderate",
                "value": f"FBS {fbs} mg/dL",
                "threshold": "Requires OGTT confirmation",
                "score": 2
            }
        }
    
    return None


def _evaluate_age(age: int, verbose: bool) -> Optional[Dict]:
    """Evaluate age-related risk."""
    if age < AGE_RISK_THRESHOLDS["young_primi"]["age_max"]:
        category = "young_primi"
        condition = "young_maternal_age"
        label = "Young Maternal Age"
    elif age >= AGE_RISK_THRESHOLDS["advanced_maternal_age"]["age_min"]:
        category = "advanced_maternal_age"
        condition = "advanced_maternal_age"
        label = "Advanced Maternal Age"
    else:
        return None
    
    threshold_data = AGE_RISK_THRESHOLDS[category]
    
    if verbose:
        print(f"[RULE] Age: {age} years → {label}")
    
    return {
        "condition": condition,
        "rule": condition,
        "score": threshold_data["score"],
        "flag": {
            "condition": label,
            "present": True,
            "severity": threshold_data["severity"],
            "value": f"{age} years",
            "threshold": f"{'<' if category == 'young_primi' else '≥'} {threshold_data.get('age_max') or threshold_data.get('age_min')} years",
            "score": threshold_data["score"]
        }
    }


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
        "eclampsia", "severe_pre_eclampsia", "severe_anaemia", "placenta_previa"
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
