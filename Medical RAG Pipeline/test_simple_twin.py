import requests
import json

# Simple text query test
data = {
    "query": "31-year-old woman at 28 weeks with twin pregnancy",
    "care_level": "PHC"
}

print("Testing simple text query...")
try:
    response = requests.post(
        "http://localhost:8000/assess",
        json=data,
        timeout=120
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
