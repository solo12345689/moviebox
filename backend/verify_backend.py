import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_search():
    print("Testing Search...")
    try:
        response = requests.get(f"{BASE_URL}/search", params={"query": "Avatar"})
        response.raise_for_status()
        data = response.json()
        print(f"Search Results: {len(data['results'])} items found")
        if data['results']:
            print(f"First item: {data['results'][0]}")
            return data['results'][0]['id']
    except Exception as e:
        print(f"Search failed: {e}")
    return None

def test_details(item_id):
    print(f"\nTesting Details for ID: {item_id}...")
    try:
        response = requests.get(f"{BASE_URL}/details/{item_id}")
        response.raise_for_status()
        data = response.json()
        print(f"Details: {data}")
    except Exception as e:
        print(f"Details failed: {e}")

def main():
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    item_id = test_search()
    if item_id:
        test_details(item_id)
    else:
        print("Skipping details test as search failed or returned no results")

if __name__ == "__main__":
    main()
