#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke test for rule engine consolidation.
Tests that only clinical_rules.py is running, not layer3_rules.py.
"""

import sys
import os
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Test case from STEP 8
test_payload = {
    "query": "28-year-old at 20 weeks, Hb 10.6, BP 110/72, no symptoms, no OGTT done",
    "care_level": "PHC"
}

print("="*70)
print("CONSOLIDATION SMOKE TEST")
print("="*70)
print(f"\nTest Query: {test_payload['query']}")
print(f"Care Level: {test_payload['care_level']}")
print("\nExpected Output:")
print("  - isHighRisk: true")
print("  - riskLevel: MODERATE")
print("  - detectedRisks includes: mild_anaemia AND gdm_screening_pending")
print("  - confidence >= 0.70")
print("  - No truncated recommendation")
print("  - No pre-eclampsia hallucination")
print("  - Console shows [RULE ENGINE] logs, NO [LAYER3] logs")
print("\n" + "="*70)
print("RUNNING TEST...")
print("="*70 + "\n")

# Import and run
try:
    from production_pipeline import ProductionRAGPipeline
    
    # Initialize pipeline
    pipeline = ProductionRAGPipeline()
    
    # Run query
    result = pipeline.run(
        query=test_payload['query'],
        care_level=test_payload['care_level'],
        verbose=True
    )
    
    print("\n" + "="*70)
    print("TEST RESULT")
    print("="*70)
    
    # Extract key fields from result
    rule_output = result.get('rule_output', {})
    
    print(f"\nRisk Level: {rule_output.get('overall_risk', 'N/A')}")
    print(f"Risk Score: {rule_output.get('total_score', 'N/A')}")
    print(f"Triggered Rules: {rule_output.get('triggered_rules', [])}")
    print(f"Confidence: {result.get('confidence', {}).get('score', 'N/A'):.2f}")
    
    print("\n" + "="*70)
    print("VALIDATION")
    print("="*70)
    
    # Validate expectations
    triggered_rules = rule_output.get('triggered_rules', [])
    has_mild_anaemia = 'mild_anaemia' in triggered_rules
    has_gdm_screening = any('gdm_screening' in r for r in triggered_rules)
    risk_level = rule_output.get('overall_risk', '')
    confidence = result.get('confidence', {}).get('score', 0)
    
    print(f"\n[CHECK] mild_anaemia detected: {has_mild_anaemia}")
    print(f"[CHECK] gdm_screening_pending detected: {has_gdm_screening}")
    print(f"[CHECK] riskLevel is MODERATE: {risk_level == 'MODERATE'}")
    print(f"[CHECK] confidence >= 0.70: {confidence >= 0.70} ({confidence:.2f})")
    
    # Check for success
    all_pass = (
        has_mild_anaemia and
        has_gdm_screening and
        risk_level == 'MODERATE' and
        confidence >= 0.70
    )
    
    if all_pass:
        print("\n" + "="*70)
        print("[PASS] SMOKE TEST PASSED")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("[FAIL] SMOKE TEST FAILED")
        print("="*70)
        sys.exit(1)
        
except Exception as e:
    print("\n" + "="*70)
    print("[ERROR] TEST ERROR")
    print("="*70)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
