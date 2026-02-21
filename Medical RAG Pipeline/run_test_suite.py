"""
Test Suite Runner for test1.md
Runs all 5 test cases and validates against expected outputs
"""

import requests
import json
import time
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000"

# Test case data from test1.md
TEST_CASES = {
    "TC1": {
        "name": "Topic Isolation Rule",
        "input": {
            "query": "A 28-year-old G3P2 at 30 weeks presents to a PHC with BP 150/95 mmHg, mild pedal edema, and headache for 2 days. No history of diabetes, thyroid disorder, or previous complications. Previous deliveries were uneventful vaginal births at term. Urine dipstick and labs unavailable. Fetal movements normal. Nearest FRU is 30 km away.",
            "care_level": "PHC",
            "verbose": True
        },
        "expected": {
            "overall_risk": "MODERATE",
            "total_score": 3,
            "triggered_rules": ["hypertension"],
            "age": 28,
            "systolic_bp": 150,
            "diastolic_bp": 95,
            "comorbidities": []
        },
        "answer_must_contain": [
            "suspected pre-eclampsia",
            "alpha methyl dopa",
            "refer"
        ],
        "answer_must_not_contain": [
            "gdm",
            "gestational diabetes",
            "blood glucose monitoring",
            "insulin",
            "ogtt"
        ],
        "checklist": [
            "overall_risk = MODERATE",
            "total_score = 3",
            "triggered_rules contains only hypertension",
            "comorbidities = []",
            "answer contains antihypertensive drug names",
            "answer uses 'suspected' language",
            "answer does NOT mention GDM/glucose/insulin"
        ]
    },
    "TC2": {
        "name": "Drug Completeness Rule",
        "input": {
            "query": "A 32-year-old G1P0 at 36 weeks presents with BP 144/94 mmHg recorded twice 4 hours apart. She has mild headache and 1+ proteinuria on dipstick. No prior hypertension. She is at a CHC with a medical officer available. She is not in labor. Nearest district hospital is 20 km.",
            "care_level": "CHC",
            "verbose": True
        },
        "expected": {
            "overall_risk": "HIGH",
            "age": 32,
            "gestational_age_weeks": 36,
            "systolic_bp": 144,
            "diastolic_bp": 94
        },
        "answer_must_contain": [
            "alpha methyl dopa",
            "nifedipine",
            "labetalol",
            "mgso4",
            "mild pre-eclampsia"
        ],
        "answer_must_not_contain": [
            "severe pre-eclampsia",
            "gdm"
        ],
        "checklist": [
            "overall_risk = HIGH",
            "answer contains Alpha Methyl Dopa with dose",
            "answer contains Nifedipine with dose",
            "answer contains Labetalol with dose",
            "answer contains MgSO4",
            "pre-eclampsia classified as MILD",
            "delivery timing guidance present"
        ]
    },
    "TC3": {
        "name": "Steroid Gating Rule",
        "input": {
            "query": "A 26-year-old G2P1 at 29 weeks presents with fundal height measuring 24 cm (3 cm below gestational age). BP is 118/76 mmHg, no edema, no proteinuria. Fetal movements slightly reduced. No diabetes or hypertension history. USG not available at center. Nearest referral hospital 50 km away.",
            "care_level": "PHC",
            "verbose": True
        },
        "expected": {
            "overall_risk": "MODERATE",
            "age": 26,
            "gestational_age_weeks": 29,
            "systolic_bp": 118,
            "diastolic_bp": 76,
            "comorbidities": []
        },
        "answer_must_contain": [
            "antenatal steroid",
            "suspected iugr",
            "fetal movement"
        ],
        "answer_must_not_contain": [
            "blood glucose monitoring after steroid",
            "insulin adjustment",
            "gdm"
        ],
        "checklist": [
            "IUGR flagged",
            "antenatal steroids recommended",
            "NO glucose monitoring after steroids",
            "fetal movement count guidance present",
            "BP correctly identified as NORMAL",
            "comorbidities = []"
        ]
    },
    "TC4": {
        "name": "Differential Clarity Rule",
        "input": {
            "query": "A 30-year-old G2P1 at 34 weeks presents with BP 148/96 mmHg, puffiness of face, and severe headache. No urine dipstick available. No visual disturbances or seizures yet. No prior hypertension. Fetal movements present. She is at a rural sub-center with no lab facilities. Referral hospital 60 km away.",
            "care_level": "PHC",
            "verbose": True
        },
        "expected": {
            "overall_risk": "HIGH",
            "age": 30,
            "gestational_age_weeks": 34,
            "systolic_bp": 148,
            "diastolic_bp": 96
        },
        "answer_must_contain": [
            "suspected pre-eclampsia",
            "proteinuria unconfirmed",
            "confirm at referral",
            "danger signs"
        ],
        "answer_must_not_contain": [
            "pre-eclampsia confirmed",
            "diagnosed with pre-eclampsia"
        ],
        "checklist": [
            "answer uses 'suspected' language",
            "answer states proteinuria unconfirmed",
            "answer recommends confirm at referral",
            "danger signs listed",
            "antihypertensive drugs named",
            "referral urgency communicated",
            "overall_risk = HIGH"
        ]
    },
    "TC5": {
        "name": "All Rules Combined (Regression)",
        "input": {
            "query": "A 19-year-old primigravida at 26 weeks presents with BP 160/108 mmHg, severe headache, blurring of vision, and 2+ pedal edema. She was diagnosed with GDM at 24 weeks and is on dietary management only. Urine dipstick shows 3+ proteinuria. Hb is 8.5 g/dl. Fetal movements are reduced. No seizures yet. Nearest CEmOC facility is 40 km away.",
            "care_level": "CHC",
            "verbose": True
        },
        "expected": {
            "overall_risk": "CRITICAL",
            "total_score": 10,
            "age": 19,
            "gestational_age_weeks": 26,
            "systolic_bp": 160,
            "diastolic_bp": 108,
            "hemoglobin": 8.5,
            "comorbidities": ["gdm"]
        },
        "answer_must_contain": [
            "severe pre-eclampsia",
            "mgso4",
            "nifedipine",
            "betamethasone",
            "gdm",
            "moderate anaemia",
            "adolescent"
        ],
        "answer_must_not_contain": [],
        "checklist": [
            "overall_risk = CRITICAL",
            "total_score = 10",
            "adolescent_pregnancy flagged",
            "severe pre-eclampsia classified",
            "MgSO4 loading dose specified",
            "antihypertensive drug named",
            "betamethasone recommended",
            "GDM section separate from PE section",
            "anaemia section separate",
            "NO cross-contamination",
            "EMERGENCY referral stated",
            "risk score consistent"
        ]
    }
}


def run_test_case(tc_id: str, test_data: Dict) -> Tuple[bool, Dict, List[str]]:
    """Run a single test case and validate results."""
    print(f"\n{'='*80}")
    print(f"TEST CASE {tc_id}: {test_data['name']}")
    print(f"{'='*80}")
    
    # Send request
    print(f"\n📤 Sending request...")
    print(f"Query: {test_data['input']['query'][:100]}...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/query",
            json=test_data['input'],
            timeout=120
        )
        elapsed = time.time() - start_time
        
        print(f"⏱️  Response time: {elapsed:.2f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.text}")
            return False, {}, ["Request failed"]
        
        data = response.json()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, {}, [f"Error: {e}"]
    
    # Validate results
    print(f"\n🔍 Validating results...")
    failures = []
    
    # Check expected fields
    for key, expected_value in test_data['expected'].items():
        if key in ['overall_risk', 'total_score']:
            actual_value = data['rule_output'].get(key)
        elif key in ['age', 'systolic_bp', 'diastolic_bp', 'hemoglobin', 'gestational_age_weeks', 'comorbidities']:
            actual_value = data['features'].get(key)
        elif key == 'triggered_rules':
            actual_value = data['rule_output'].get(key, [])
        else:
            actual_value = None
        
        if actual_value != expected_value:
            if key == 'triggered_rules':
                # Check if expected rules are subset of actual
                if not all(rule in actual_value for rule in expected_value):
                    failures.append(f"❌ {key}: expected {expected_value}, got {actual_value}")
                else:
                    print(f"✅ {key}: {actual_value}")
            else:
                failures.append(f"❌ {key}: expected {expected_value}, got {actual_value}")
        else:
            print(f"✅ {key}: {actual_value}")
    
    # Check answer content
    answer_lower = data['answer'].lower()
    
    print(f"\n📝 Checking answer content...")
    for phrase in test_data['answer_must_contain']:
        if phrase.lower() not in answer_lower:
            failures.append(f"❌ Answer missing required phrase: '{phrase}'")
            print(f"❌ Missing: '{phrase}'")
        else:
            print(f"✅ Contains: '{phrase}'")
    
    for phrase in test_data['answer_must_not_contain']:
        if phrase.lower() in answer_lower:
            failures.append(f"❌ Answer contains forbidden phrase: '{phrase}'")
            print(f"❌ Should not contain: '{phrase}'")
        else:
            print(f"✅ Does not contain: '{phrase}'")
    
    # Print checklist
    print(f"\n📋 Checklist:")
    for item in test_data['checklist']:
        print(f"   {item}")
    
    # Summary
    passed = len(failures) == 0
    if passed:
        print(f"\n✅ TEST {tc_id} PASSED")
    else:
        print(f"\n❌ TEST {tc_id} FAILED")
        print(f"\nFailures:")
        for failure in failures:
            print(f"  {failure}")
    
    return passed, data, failures


def run_all_tests():
    """Run all test cases and generate report."""
    print("\n" + "="*80)
    print("MEDICAL RAG TEST SUITE - test1.md")
    print("="*80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start: python api_server.py")
            return
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server. Please start: python api_server.py")
        return
    
    results = {}
    all_passed = True
    
    # Run each test case
    for tc_id in ["TC1", "TC2", "TC3", "TC4", "TC5"]:
        passed, data, failures = run_test_case(tc_id, TEST_CASES[tc_id])
        results[tc_id] = {
            "passed": passed,
            "data": data,
            "failures": failures
        }
        all_passed = all_passed and passed
        
        # Small delay between tests
        time.sleep(2)
    
    # Generate summary report
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for r in results.values() if r['passed'])
    total_count = len(results)
    score = (passed_count / total_count) * 100
    
    for tc_id, result in results.items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status}: {tc_id} - {TEST_CASES[tc_id]['name']}")
        if not result['passed']:
            print(f"       Failures: {len(result['failures'])}")
    
    print(f"\n📊 Score: {passed_count}/{total_count} tests passed ({score:.0f}%)")
    
    if score >= 95:
        print(f"🎉 EXCELLENT! Target achieved (95%+)")
    elif score >= 80:
        print(f"✅ GOOD! Close to target (80%+)")
    elif score >= 60:
        print(f"⚠️  NEEDS IMPROVEMENT (60%+)")
    else:
        print(f"❌ CRITICAL ISSUES (<60%)")
    
    print("\n" + "="*80)
    
    # Save detailed results
    with open('test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed_count,
                'total': total_count,
                'score': score,
                'all_passed': all_passed
            },
            'results': {
                tc_id: {
                    'passed': r['passed'],
                    'failures': r['failures']
                }
                for tc_id, r in results.items()
            }
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to: test_results.json")
    
    return all_passed


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test case
        tc_id = sys.argv[1].upper()
        if tc_id in TEST_CASES:
            run_test_case(tc_id, TEST_CASES[tc_id])
        else:
            print(f"Unknown test case: {tc_id}")
            print(f"Available: {', '.join(TEST_CASES.keys())}")
    else:
        # Run all tests
        run_all_tests()
