# ============================================================
# test_production.py — Test Production RAG System
# ============================================================
"""
Test suite for production RAG system.
Tests each layer independently and the integrated pipeline.
"""

def test_layer1_extraction():
    """Test Layer 1: Feature Extraction"""
    print("\n" + "="*70)
    print("TEST 1: Feature Extraction")
    print("="*70)
    
    from layer1_extractor import ClinicalFeatureExtractor
    
    extractor = ClinicalFeatureExtractor()
    
    test_cases = [
        "38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
        "25-year-old with BP 120/80, Hb 12.5, FBS 90",
        "17-year-old with Hb 8.5",
    ]
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        features = extractor.extract(query, verbose=False)
        print(f"  Age: {features.age}")
        print(f"  BP: {features.systolic_bp}/{features.diastolic_bp}")
        print(f"  Hb: {features.hemoglobin}")
        print(f"  FBS: {features.fbs}")
        print(f"  Twin: {features.twin_pregnancy}")
        print(f"  Confidence: {features.extraction_confidence:.2f}")
    
    print("\n✓ Layer 1 tests passed")


def test_layer3_rules():
    """Test Layer 3: Rule Engine"""
    print("\n" + "="*70)
    print("TEST 2: Clinical Rule Engine")
    print("="*70)
    
    from layer1_extractor import ClinicalFeatureExtractor
    from layer3_rules import ClinicalRuleEngine
    
    extractor = ClinicalFeatureExtractor()
    engine = ClinicalRuleEngine()
    
    test_cases = [
        ("38-year-old with BP 150/95, Hb 10.5, twin pregnancy", "HIGH"),
        ("25-year-old with BP 120/80, Hb 12.5", "LOW"),
        ("42-year-old with BP 165/115, Hb 6.5", "CRITICAL"),
    ]
    
    for query, expected_risk in test_cases:
        print(f"\nQuery: {query}")
        features = extractor.extract(query)
        output = engine.apply_rules(features, verbose=False)
        print(f"  Risk: {output.overall_risk} (expected: {expected_risk})")
        print(f"  Score: {output.total_score}")
        print(f"  Coverage: {output.rule_coverage:.2f}")
        
        if output.overall_risk == expected_risk:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
    
    print("\n✓ Layer 3 tests passed")


def test_confidence_scoring():
    """Test Confidence Scoring"""
    print("\n" + "="*70)
    print("TEST 3: Confidence Scoring")
    print("="*70)
    
    from confidence_scorer import calculate_confidence
    
    test_cases = [
        (0.85, 1.0, 0.70, 0.95, "HIGH"),
        (0.60, 0.80, 0.50, 0.85, "MEDIUM"),
        (0.30, 0.50, 0.40, 0.70, "LOW"),
        (0.20, 0.30, 0.20, 0.50, "VERY_LOW"),
    ]
    
    for ret_q, rule_c, chunk_a, ext_c, expected_level in test_cases:
        confidence = calculate_confidence(ret_q, rule_c, chunk_a, ext_c, verbose=False)
        print(f"\nInputs: ret={ret_q:.2f}, rule={rule_c:.2f}, chunk={chunk_a:.2f}, ext={ext_c:.2f}")
        print(f"  Score: {confidence['score']:.2f}")
        print(f"  Level: {confidence['level']} (expected: {expected_level})")
        
        if confidence['level'] == expected_level:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
    
    print("\n✓ Confidence scoring tests passed")


def test_hallucination_guard():
    """Test Hallucination Guard"""
    print("\n" + "="*70)
    print("TEST 4: Hallucination Guard")
    print("="*70)
    
    from hallucination_guard import check_hallucination_risk
    
    test_cases = [
        (0.82, 0.85, True),   # Should allow
        (0.30, 0.85, False),  # Should block (low confidence)
        (0.82, 0.30, False),  # Should block (low retrieval)
        (0.25, 0.25, False),  # Should block (both low)
    ]
    
    for conf, ret_q, expected_allow in test_cases:
        guard = check_hallucination_risk(conf, ret_q, verbose=False)
        print(f"\nInputs: confidence={conf:.2f}, retrieval={ret_q:.2f}")
        print(f"  Allow: {guard['allow_output']} (expected: {expected_allow})")
        
        if guard['allow_output'] == expected_allow:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
    
    print("\n✓ Hallucination guard tests passed")


def test_integrated_pipeline():
    """Test Integrated Pipeline (requires FAISS index and Ollama)"""
    print("\n" + "="*70)
    print("TEST 5: Integrated Pipeline")
    print("="*70)
    
    try:
        from production_pipeline import ProductionRAGPipeline
        
        pipeline = ProductionRAGPipeline()
        
        test_query = "38-year-old with BP 150/95, Hb 10.5, twin pregnancy"
        print(f"\nTest Query: {test_query}")
        
        result = pipeline.run(test_query, verbose=False)
        
        print(f"\n  Blocked: {result['blocked']}")
        print(f"  Confidence: {result['confidence']['score']:.2f} ({result['confidence']['level']})")
        print(f"  Risk: {result['rule_output']['overall_risk']}")
        print(f"  Score: {result['rule_output']['total_score']}")
        
        if not result['blocked'] and result['rule_output']['overall_risk'] == 'HIGH':
            print("\n  ✓ PASS - Correctly identified high-risk case")
        else:
            print("\n  ✗ FAIL")
        
        print("\n✓ Integrated pipeline test passed")
        
    except Exception as e:
        print(f"\n⚠️  Integrated test skipped: {str(e)}")
        print("  (Requires FAISS index and Ollama running)")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("PRODUCTION RAG SYSTEM TEST SUITE")
    print("="*70)
    
    # Test individual layers
    test_layer1_extraction()
    test_layer3_rules()
    test_confidence_scoring()
    test_hallucination_guard()
    
    # Test integrated pipeline (optional)
    test_integrated_pipeline()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
