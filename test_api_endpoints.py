import requests
import json

# First, search for a TV series
print("Searching for Breaking Bad...")
response = requests.get("http://localhost:8000/api/search", params={"query": "Breaking Bad", "type": "series"})
print(f"Search status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if data.get("results"):
        first_item = data["results"][0]
        print(f"\nFirst result: {first_item['title']}")
        print(f"Type: {first_item['type']}")
        print(f"ID: {first_item['id']}")
        
        # Now get details
        print(f"\nGetting details for {first_item['id']}...")
        details_response = requests.get(f"http://localhost:8000/api/details/{first_item['id']}")
        print(f"Details status: {details_response.status_code}")
        
        if details_response.status_code == 200:
            details = details_response.json()
            print(f"\nDetails:")
            print(json.dumps(details, indent=2))
        else:
            print(f"Details error: {details_response.text}")
    else:
        print("No results found")
else:
    print(f"Search error: {response.text}")
