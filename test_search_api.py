import requests
import json

# Test the search endpoint
print("Testing search endpoint...")
try:
    response = requests.get("http://localhost:8000/api/search", params={"query": "inception", "type": "all"}, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
