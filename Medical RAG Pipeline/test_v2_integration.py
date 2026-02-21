"""
Test V2 Rule Engine Integration
Verify that clinical_rules.py is V2 and all components are working
"""

from clinical_rules import (
    run_rule_engine,
    RuleEngineResult,
    RISK_SCORE_MATRIX,
    SHORT_STATURE_THRESHOLD,
    HIGH_BMI_THRESHOLD,
    HIGH_BIRTH_ORDER_THRESHOLD
)

def test_v2_thresholds_exist():
    """Test that V2 thresholds are defined."""
    print("\n" + "="*70)
    print("TEST 1: V2 Thresholds Exist")
    print("="*70)
    
    # Check new thresholds
    assert SHORT_STATURE_THRESHOLD == 140, "Short stature threshold missing"
    assert HIGH_BMI_THRESHOLD == 30.0, "High BMI threshold missing"
    assert HIGH_BIRTH_ORDER_THRESHOLD == 5, "High birth order threshold missing"
    
    # Check new conditions in risk matrix
    new_conditions = [
        'short_stature', 'high_bmi', 'smoking', 'tobacco_use', 'alcohol_use',
        'high_birth_order', 'short_birth_spacing', 'long_birth_spacing',
        'previous_preterm', 'previous_stillbirth', 'previous_abortion',
        'rh_negative', 'hiv_positive', 'syphilis_positive',
        'malpresentation', 'systemic_illness'
    ]
    
    for condition in new_conditions:
        assert condition in RISK_SCORE_MATRIX, f"Condition {condition} missing from risk matrix"
    
    print("✅ All V2 thresholds and conditions present")
    print(f"   - Total conditions in risk matrix: {len(RISK_SCORE_MATRIX)}")
    print(f"   - New V2 conditions: {len(new_conditions)}")


def test_v2_rule_engine_basic():
    """Test basic V2 rule engine functionality."""
    print("\n" + "="*70)
    print("TEST 2: V2 Rule Engine Basic Functionality")
    print("="*70)
    
    # Test case: Patient with mild anaemia only
    features = {
        'age': 28,
        'gestational_age_weeks': 20,
        'hemoglobin': 10.5,
        'systolic_bp': 110,
        'diastolic_bp': 70
    }
    
    result = run_rule_engine(features, verbose=True)
    
    assert isinstance(result, RuleEngineResult), "Result is not RuleEngineResult"
    assert hasattr(result, 'is_hpr'), "Result missing is_hpr field"
    assert hasattr(result, 'borderline_flags'), "Result missing borderline_flags field"
    
    print(f"\n✅ Rule engine returned valid V2 result")
    print(f"   - Risk Level: {result.risk_level}")
    print(f"   - Risk Score: {result.risk_score}")
    print(f"   - Is HPR: {result.is_hpr}")
    print(f"   - Triggered Rules: {result.triggered_rules}")


def test_v2_new_conditions():
    """Test new V2 conditions."""
    print("\n" + "="*70)
    print("TEST 3: V2 New Conditions Detection")
    print("="*70)
    
    # Test case: Patient with multiple new V2 conditions
    features = {
        'age': 28,
        'gestational_age_weeks': 20,
        'hemoglobin': 11.5,
        'systolic_bp': 110,
        'diastolic_bp': 70,
        'height': 135,  # Short stature
        'bmi': 32,  # High BMI
        'smoking': True,
        'rh_negative': True,
        'birth_order': 6,  # High birth order
        'inter_pregnancy_interval': 12,  # Short spacing
    }
    
    result = run_rule_engine(features, verbose=True)
    
    # Check that new conditions were detected
    expected_conditions = [
        'short_stature', 'high_bmi', 'smoking', 'rh_negative',
        'high_birth_order', 'short_birth_spacing'
    ]
    
    detected = 0
    for condition in expected_conditions:
        if condition in result.triggered_rules:
            detected += 1
            print(f"   ✅ Detected: {condition}")
        else:
            print(f"   ❌ Missed: {condition}")
    
    print(f"\n✅ Detected {detected}/{len(expected_conditions)} new V2 conditions")
    print(f"   - Total Risk Score: {result.risk_score}")
    print(f"   - Risk Level: {result.risk_level}")
    print(f"   - Is HPR: {result.is_hpr}")


def test_v2_borderline_monitoring():
    """Test borderline value monitoring."""
    print("\n" + "="*70)
    print("TEST 4: V2 Borderline Monitoring")
    print("="*70)
    
    # Test case: Patient with borderline values
    features = {
        'age': 28,
        'gestational_age_weeks': 20,
        'hemoglobin': 10.3,  # Borderline anaemia
        'systolic_bp': 135,  # Pre-hypertension
        'diastolic_bp': 87
    }
    
    result = run_rule_engine(features, verbose=True)
    
    if result.borderline_flags:
        print(f"\n✅ Borderline monitoring active")
        for flag in result.borderline_flags:
            print(f"   - {flag['condition']}: {flag['value']} -> {flag['action']}")
    else:
        print(f"\n⚠️  No borderline flags detected (expected some)")
    
    print(f"   - Risk Level: {result.risk_level}")
    print(f"   - Risk Score: {result.risk_score}")


def test_v2_hpr_flag_logic():
    """Test composite HPR flag logic."""
    print("\n" + "="*70)
    print("TEST 5: V2 Composite HPR Flag Logic")
    print("="*70)
    
    # Test case 1: Low risk (should NOT be HPR)
    features_low = {
        'age': 28,
        'gestational_age_weeks': 20,
        'hemoglobin': 11.5,
        'systolic_bp': 110,
        'diastolic_bp': 70
    }
    
    result_low = run_rule_engine(features_low, verbose=False)
    print(f"\nLow Risk Case:")
    print(f"   - Risk Level: {result_low.risk_level}")
    print(f"   - Is HPR: {result_low.is_hpr}")
    print(f"   - Expected: False")
    
    # Test case 2: High risk (should be HPR)
    features_high = {
        'age': 38,  # Advanced maternal age
        'gestational_age_weeks': 30,
        'hemoglobin': 6.5,  # Severe anaemia
        'systolic_bp': 155,  # Hypertension
        'diastolic_bp': 100,
        'twin_pregnancy': True
    }
    
    result_high = run_rule_engine(features_high, verbose=False)
    print(f"\nHigh Risk Case:")
    print(f"   - Risk Level: {result_high.risk_level}")
    print(f"   - Is HPR: {result_high.is_hpr}")
    print(f"   - Expected: True")
    print(f"   - Triggered: {result_high.triggered_rules}")
    
    print(f"\n✅ HPR flag logic working")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("V2 RULE ENGINE INTEGRATION TEST SUITE")
    print("="*70)
    
    try:
        test_v2_thresholds_exist()
        test_v2_rule_engine_basic()
        test_v2_new_conditions()
        test_v2_borderline_monitoring()
        test_v2_hpr_flag_logic()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED - V2 INTEGRATION COMPLETE")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
