#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ONLY the rule engine consolidation without running full RAG pipeline.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*70)
print("RULE ENGINE CONSOLIDATION TEST")
print("="*70)

# Test that clinical_rules.py works
print("\n[TEST 1] Import clinical_rules.py...")
try:
    from clinical_rules import run_rule_engine, RuleEngineResult
    print("[PASS] clinical_rules.py imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import: {e}")
    sys.exit(1)

# Test that layer3_rules is NOT being used
print("\n[TEST 2] Verify layer3_rules is not imported in production_pipeline.py...")
try:
    with open('production_pipeline.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'from layer3_rules import' in content and not content.count('# from layer3_rules'):
            print("[FAIL] layer3_rules is still being imported!")
            sys.exit(1)
        else:
            print("[PASS] layer3_rules is not imported")
except Exception as e:
    print(f"[FAIL] Error reading file: {e}")
    sys.exit(1)

# Test rule engine with sample data
print("\n[TEST 3] Run rule engine with test data...")
try:
    test_features = {
        'age': 28,
        'gestational_age_weeks': 20,
        'hemoglobin': 10.6,
        'systolic_bp': 110,
        'diastolic_bp': 72,
        'fbs': None,
        'ogtt_2hr_pg': None,
        'proteinuria': False,
        'seizures': False,
        'twin_pregnancy': False,
        'prior_cesarean': False,
        'placenta_previa': False,
    }
    
    result = run_rule_engine(test_features, verbose=True)
    
    print(f"\n[RESULT] Risk Level: {result.risk_level}")
    print(f"[RESULT] Risk Score: {result.risk_score}")
    print(f"[RESULT] Triggered Rules: {result.triggered_rules}")
    print(f"[RESULT] Rule Coverage: {result.rule_coverage}")
    print(f"[RESULT] Confirmed Conditions: {result.confirmed_conditions}")
    print(f"[RESULT] Suspected Conditions: {result.suspected_conditions}")
    
    # Validate expectations
    has_mild_anaemia = 'mild_anaemia' in result.triggered_rules
    has_gdm_screening = any('gdm_screening' in r for r in result.triggered_rules)
    
    print("\n" + "="*70)
    print("VALIDATION")
    print("="*70)
    print(f"[CHECK] mild_anaemia detected: {has_mild_anaemia}")
    print(f"[CHECK] gdm_screening_pending detected: {has_gdm_screening}")
    print(f"[CHECK] rule_coverage exists: {hasattr(result, 'rule_coverage')}")
    print(f"[CHECK] rule_coverage value: {result.rule_coverage}")
    
    if has_mild_anaemia and has_gdm_screening and result.rule_coverage == 1.0:
        print("\n" + "="*70)
        print("[PASS] RULE ENGINE TEST PASSED")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("[FAIL] RULE ENGINE TEST FAILED")
        print("="*70)
        sys.exit(1)
        
except Exception as e:
    print(f"\n[FAIL] Error running rule engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
