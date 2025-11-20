import requests
import json
import time

# Wait a bit for server to be ready
time.sleep(2)

# Test the search endpoint
print("Testing search endpoint with content_type parameter...")
try:
    response = requests.get(
        "http://localhost:8000/api/search", 
        params={"query": "inception", "content_type": "all"}, 
        timeout=30
    )
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse Headers: {dict(response.headers)}")
    print(f"\nResponse Text: {response.text[:1000]}")  # First 1000 chars
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess! Found {len(data.get('results', []))} results")
        if data.get('results'):
            print(f"First result: {data['results'][0]['title']}")
    else:
        print(f"\nError response: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\nConnection Error: {e}")
    print("Is the backend server running on port 8000?")
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
