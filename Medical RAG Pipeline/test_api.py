"""
Test client for Medical RAG API
"""

import requests
import json
from typing import Dict

# API base URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_system_info():
    """Test system info endpoint."""
    print("\n" + "="*70)
    print("TEST 2: System Info")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/system-info")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"System: {data['system']}")
    print(f"Version: {data['version']}")
    print(f"Capabilities: {len(data['capabilities'])} features")
    print(f"Clinical Rules: {len(data['clinical_rules'])} rules")
    print(f"Safety Features: {len(data['safety_features'])} features")
    return response.status_code == 200


def test_care_levels():
    """Test care levels endpoint."""
    print("\n" + "="*70)
    print("TEST 3: Care Levels")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/care-levels")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    for level, info in data['care_levels'].items():
        print(f"\n{level}: {info['name']}")
        print(f"  Allowed: {', '.join(info['allowed_actions'])}")
    return response.status_code == 200


def test_query(query: str, care_level: str = "PHC", verbose: bool = False):
    """Test query endpoint."""
    print("\n" + "="*70)
    print(f"TEST: Clinical Query")
    print("="*70)
    print(f"Query: {query}")
    print(f"Care Level: {care_level}")
    
    payload = {
        "query": query,
        "care_level": care_level,
        "verbose": verbose
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n{'='*70}")
        print("RESPONSE SUMMARY")
        print(f"{'='*70}")
        
        print(f"\nSuccess: {data['success']}")
        print(f"Blocked: {data['blocked']}")
        print(f"Processing Time: {data['processing_time_ms']:.2f}ms")
        
        print(f"\n--- CLINICAL FEATURES ---")
        features = data['features']
        if features['age']:
            print(f"Age: {features['age']} years")
        if features['gestational_age_weeks']:
            print(f"Gestational Age: {features['gestational_age_weeks']} weeks")
        if features['systolic_bp']:
            print(f"BP: {features['systolic_bp']}/{features['diastolic_bp']} mmHg")
        if features['hemoglobin']:
            print(f"Hb: {features['hemoglobin']} g/dL")
        if features['twin_pregnancy']:
            print(f"Twin Pregnancy: Yes")
        print(f"Extraction Confidence: {features['extraction_confidence']:.2f}")
        
        print(f"\n--- RISK ASSESSMENT ---")
        rule_output = data['rule_output']
        print(f"Overall Risk: {rule_output['overall_risk']}")
        print(f"Risk Score: {rule_output['total_score']}")
        print(f"Rule Coverage: {rule_output['rule_coverage']:.2f}")
        print(f"Triggered Rules: {', '.join(rule_output['triggered_rules'])}")
        
        if rule_output['risk_flags']:
            print(f"\nRisk Flags:")
            for flag in rule_output['risk_flags']:
                print(f"  • {flag['condition']}: {flag['value']} (Severity: {flag['severity']})")
        
        print(f"\n--- CONFIDENCE ---")
        confidence = data['confidence']
        print(f"Score: {confidence['score']:.2f} ({confidence['level']})")
        if confidence.get('ceiling_applied'):
            print(f"Ceiling Applied: {', '.join(confidence['ceiling_applied'])}")
        print(f"Breakdown:")
        for key, value in confidence['breakdown'].items():
            print(f"  - {key}: {value:.2f}")
        
        if not data['blocked'] and data['retrieval_stats']:
            print(f"\n--- RETRIEVAL STATS ---")
            stats = data['retrieval_stats']
            print(f"FAISS chunks: {stats['faiss_count']}")
            print(f"BM25 chunks: {stats['bm25_count']}")
            print(f"Final chunks: {stats['final_count']}")
            print(f"Retrieval Quality: {stats['retrieval_quality']:.2f}")
        
        print(f"\n--- ANSWER ---")
        print(data['answer'][:500] + "..." if len(data['answer']) > 500 else data['answer'])
        
        return True
    else:
        print(f"Error: {response.json()}")
        return False


def run_test_suite():
    """Run complete test suite."""
    print("\n" + "="*70)
    print("MEDICAL RAG API - TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: System info
    results.append(("System Info", test_system_info()))
    
    # Test 3: Care levels
    results.append(("Care Levels", test_care_levels()))
    
    # Test 4: High-risk case
    results.append((
        "High-Risk Query",
        test_query("38-year-old with BP 150/95, Hb 10.5, twin pregnancy", "PHC")
    ))
    
    # Test 5: Moderate-risk case
    results.append((
        "Moderate-Risk Query",
        test_query("28-year-old with Hb 10.5", "PHC")
    ))
    
    # Test 6: Young maternal age
    results.append((
        "Young Maternal Age",
        test_query("19-year-old at 8 weeks with Hb 7.5, BP 145/95", "PHC")
    ))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Single query test
        query = " ".join(sys.argv[1:])
        test_query(query)
    else:
        # Full test suite
        run_test_suite()
