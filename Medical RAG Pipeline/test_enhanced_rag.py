# ============================================================
# test_enhanced_rag.py — Test suite for enhanced RAG pipeline
# ============================================================
"""
Test suite to validate the enhanced RAG system.
Tests feature extraction, risk scoring, and end-to-end pipeline.
"""

from clinical_preprocessor import ClinicalPreprocessor
from clinical_risk_scorer import ClinicalRiskScorer


def test_feature_extraction():
    """Test clinical feature extraction."""
    print("\n" + "="*70)
    print("TEST 1: Feature Extraction")
    print("="*70)
    
    preprocessor = ClinicalPreprocessor()
    
    test_cases = [
        {
            'query': "38-year-old pregnant woman with BP 150/95 and Hb 10.5",
            'expected': {
                'age': 38,
                'age_risk': 'advanced_maternal_age',
                'systolic_bp': 150,
                'diastolic_bp': 95,
                'bp_risk': 'hypertensive',
                'hemoglobin': 10.5,
                'anemia_risk': 'mild_anemia',
            }
        },
        {
            'query': "25-year-old with normal vitals, Hb 12.5 g/dL",
            'expected': {
                'age': 25,
                'age_risk': 'normal_age',
                'hemoglobin': 12.5,
                'anemia_risk': 'normal_hemoglobin',
            }
        },
        {
            'query': "Twin pregnancy with previous cesarean section",
            'expected': {
                'twin_pregnancy': True,
                'previous_cesarean': True,
            }
        },
        {
            'query': "17-year-old adolescent with Hb 8.5",
            'expected': {
                'age': 17,
                'age_risk': 'teenage_pregnancy',
                'hemoglobin': 8.5,
                'anemia_risk': 'moderate_anemia',
            }
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test['query']}")
        result = preprocessor.process_query(test['query'])
        features = result['extracted_features']
        
        all_match = True
        for key, expected_value in test['expected'].items():
            actual_value = getattr(features, key, None)
            if actual_value != expected_value:
                print(f"  ❌ FAIL: {key} = {actual_value}, expected {expected_value}")
                all_match = False
                failed += 1
            else:
                print(f"  ✅ PASS: {key} = {actual_value}")
        
        if all_match:
            passed += 1
            print(f"  ✅ Test Case {i} PASSED")
        else:
            print(f"  ❌ Test Case {i} FAILED")
    
    print(f"\n{'='*70}")
    print(f"Feature Extraction: {passed} passed, {failed} failed")
    print(f"{'='*70}")
    
    return passed, failed


def test_risk_scoring():
    """Test clinical risk scoring."""
    print("\n" + "="*70)
    print("TEST 2: Risk Scoring")
    print("="*70)
    
    preprocessor = ClinicalPreprocessor()
    scorer = ClinicalRiskScorer()
    
    test_cases = [
        {
            'query': "38-year-old with BP 150/95",
            'expected_risk': 'high',  # Age +3, Hypertension +3 = 6
            'min_score': 5,
        },
        {
            'query': "25-year-old with normal vitals",
            'expected_risk': 'low',
            'max_score': 1,
        },
        {
            'query': "Twin pregnancy with previous cesarean",
            'expected_risk': 'high',  # Twins +3, Previous CS +2 = 5
            'min_score': 5,
        },
        {
            'query': "42-year-old with Hb 6.5 and diabetes",
            'expected_risk': 'critical',  # Age +3, Severe anemia +3, Diabetes +3 = 9
            'min_score': 8,
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test['query']}")
        
        # Extract features
        result = preprocessor.process_query(test['query'])
        features = result['extracted_features']
        
        # Score risk
        assessment = scorer.score_risk(features)
        
        print(f"  Risk Level: {assessment.risk_level.upper()}")
        print(f"  Risk Score: {assessment.total_score}")
        print(f"  Risk Factors: {len(assessment.risk_factors)}")
        
        # Check expectations
        risk_match = assessment.risk_level == test['expected_risk']
        score_match = True
        
        if 'min_score' in test:
            score_match = assessment.total_score >= test['min_score']
        if 'max_score' in test:
            score_match = assessment.total_score <= test['max_score']
        
        if risk_match and score_match:
            print(f"  ✅ Test Case {i} PASSED")
            passed += 1
        else:
            print(f"  ❌ Test Case {i} FAILED")
            if not risk_match:
                print(f"     Expected risk: {test['expected_risk']}, got: {assessment.risk_level}")
            if not score_match:
                print(f"     Score out of expected range")
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"Risk Scoring: {passed} passed, {failed} failed")
    print(f"{'='*70}")
    
    return passed, failed


def test_query_rewriting():
    """Test query rewriting for better retrieval."""
    print("\n" + "="*70)
    print("TEST 3: Query Rewriting")
    print("="*70)
    
    preprocessor = ClinicalPreprocessor()
    
    test_cases = [
        {
            'query': "38-year-old pregnant woman",
            'should_contain': ['advanced maternal age', 'elderly gravida'],
        },
        {
            'query': "Low Hb of 9.5",
            'should_contain': ['anaemia', 'anemia', 'hemoglobin'],
        },
        {
            'query': "High BP 150/95",
            'should_contain': ['hypertension', 'blood pressure'],
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test['query']}")
        
        result = preprocessor.process_query(test['query'])
        rewritten = result['rewritten_query'].lower()
        
        print(f"  Original: {test['query']}")
        print(f"  Rewritten: {rewritten[:150]}...")
        
        all_found = True
        for term in test['should_contain']:
            if term.lower() in rewritten:
                print(f"  ✅ Contains: '{term}'")
            else:
                print(f"  ❌ Missing: '{term}'")
                all_found = False
        
        if all_found:
            print(f"  ✅ Test Case {i} PASSED")
            passed += 1
        else:
            print(f"  ❌ Test Case {i} FAILED")
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"Query Rewriting: {passed} passed, {failed} failed")
    print(f"{'='*70}")
    
    return passed, failed


def test_end_to_end():
    """Test end-to-end pipeline (requires FAISS index and Ollama)."""
    print("\n" + "="*70)
    print("TEST 4: End-to-End Pipeline (Optional)")
    print("="*70)
    
    try:
        from enhanced_rag_pipeline import EnhancedRAGPipeline
        
        print("\nInitializing pipeline...")
        pipeline = EnhancedRAGPipeline()
        
        test_query = "38-year-old with BP 150/95 and Hb 10.5"
        print(f"\nTest Query: {test_query}")
        
        print("\nRunning pipeline...")
        result = pipeline.run(test_query, debug=True, verbose=False)
        
        # Check result structure
        assert 'answer' in result, "Missing 'answer' in result"
        assert 'risk_assessment' in result, "Missing 'risk_assessment' in result"
        assert 'confidence' in result, "Missing 'confidence' in result"
        
        # Check risk assessment
        risk = result['risk_assessment']
        assert risk['risk_level'] in ['low', 'moderate', 'high', 'critical'], "Invalid risk level"
        assert risk['total_score'] >= 0, "Invalid risk score"
        
        print(f"\n✅ Pipeline executed successfully")
        print(f"   Risk Level: {risk['risk_level'].upper()}")
        print(f"   Risk Score: {risk['total_score']}")
        print(f"   Confidence: {result['confidence'].upper()}")
        print(f"   Answer Length: {len(result['answer'])} chars")
        
        return 1, 0
        
    except ImportError:
        print("\n⚠️  Skipping end-to-end test (FAISS index not available)")
        return 0, 0
    except Exception as e:
        print(f"\n❌ End-to-end test failed: {str(e)}")
        return 0, 1


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ENHANCED RAG SYSTEM TEST SUITE")
    print("="*70)
    
    total_passed = 0
    total_failed = 0
    
    # Test 1: Feature Extraction
    passed, failed = test_feature_extraction()
    total_passed += passed
    total_failed += failed
    
    # Test 2: Risk Scoring
    passed, failed = test_risk_scoring()
    total_passed += passed
    total_failed += failed
    
    # Test 3: Query Rewriting
    passed, failed = test_query_rewriting()
    total_passed += passed
    total_failed += failed
    
    # Test 4: End-to-End (optional)
    passed, failed = test_end_to_end()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n✅ ALL TESTS PASSED")
    else:
        print(f"\n❌ {total_failed} TESTS FAILED")
    
    print("="*70)


if __name__ == "__main__":
    main()
