"""
Test script for simplified /assess endpoint
Demonstrates the clean JSON output format
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test cases
test_cases = [
    {
        "name": "Severe Anemia + Advanced Age + Hypertension",
        "query": "A 38-year-old pregnant woman at 32 weeks with BP 155/98 mmHg and Hb 6.2 g/dL. She has severe headache and pedal edema.",
        "care_level": "PHC"
    },
    {
        "name": "Normal Pregnancy",
        "query": "A 26-year-old G2P1 at 28 weeks with BP 118/76 mmHg, Hb 11.5 g/dL, no complaints. Previous delivery was normal.",
        "care_level": "PHC"
    },
    {
        "name": "Teenage Pregnancy with Mild Anemia",
        "query": "A 17-year-old primigravida at 24 weeks with BP 110/70 mmHg and Hb 10.2 g/dL. No other complications.",
        "care_level": "ASHA"
    },
    {
        "name": "Twin Pregnancy + GDM",
        "query": "A 30-year-old woman at 30 weeks with twin pregnancy. FBS is 98 mg/dL. BP 130/85 mmHg, Hb 10.8 g/dL.",
        "care_level": "CHC"
    }
]

def test_assess_endpoint():
    """Test the simplified /assess endpoint."""
    print("="*80)
    print("TESTING SIMPLIFIED /assess ENDPOINT")
    print("="*80)
    
    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start: python api_server.py")
            return
        print("✅ Server is running\n")
    except:
        print("❌ Cannot connect to server. Please start: python api_server.py")
        return
    
    # Run test cases
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"Query: {test['query'][:80]}...")
        print(f"Care Level: {test['care_level']}")
        
        try:
            # Send request
            response = requests.post(
                f"{BASE_URL}/assess",
                json={
                    "query": test['query'],
                    "care_level": test['care_level'],
                    "verbose": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Pretty print result
                print(f"\n📊 RESULT:")
                print(json.dumps(result, indent=2))
                
                # Validate structure
                required_fields = ['isHighRisk', 'riskLevel', 'detectedRisks', 'explanation', 'confidence', 'recommendation']
                missing = [f for f in required_fields if f not in result]
                
                if missing:
                    print(f"\n⚠️  Missing fields: {missing}")
                else:
                    print(f"\n✅ All required fields present")
                    
                    # Show key metrics
                    print(f"\n📈 KEY METRICS:")
                    print(f"   High Risk: {'YES' if result['isHighRisk'] else 'NO'}")
                    print(f"   Risk Level: {result['riskLevel']}")
                    print(f"   Confidence: {result['confidence']:.2f}")
                    print(f"   Detected Risks: {len(result['detectedRisks'])}")
                    if result['detectedRisks']:
                        for risk in result['detectedRisks']:
                            print(f"      • {risk}")
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"\n⏱️  Request timed out (>120s)")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")


def show_example_output():
    """Show example of expected output format."""
    print("\n" + "="*80)
    print("EXPECTED OUTPUT FORMAT")
    print("="*80)
    
    example = {
        "isHighRisk": True,
        "riskLevel": "HIGH",
        "detectedRisks": [
            "Severe anemia",
            "Advanced maternal age",
            "Hypertension"
        ],
        "explanation": "Patient has Hb < 7 indicating severe anemia, age > 35, and elevated BP suggesting preeclampsia risk.",
        "confidence": 0.93,
        "recommendation": "Immediate obstetric consultation recommended."
    }
    
    print(json.dumps(example, indent=2))
    print("="*80)


if __name__ == "__main__":
    show_example_output()
    test_assess_endpoint()
