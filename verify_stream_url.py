import requests
import json

API_URL = "http://localhost:8000/api"

def test_stream_url_mode():
    print("Testing /stream with mode='url'...")
    
    # Use a known query, e.g., "Big Buck Bunny" or "Sintel" if available, or just "Naruto"
    # We need a valid item first.
    
    # 1. Search
    print("Searching for 'Naruto'...")
    search_res = requests.get(f"{API_URL}/search", params={"query": "Naruto", "content_type": "anime"})
    if search_res.status_code != 200:
        print(f"Search failed: {search_res.text}")
        return
        
    data = search_res.json()
    if not data.get("results"):
        print("No results found")
        return
        
    item = data["results"][0]
    print(f"Found item: {item['title']} (ID: {item['id']})")
    
    # 2. Request Stream URL
    print("Requesting stream URL...")
    stream_url = f"{API_URL}/stream"
    params = {
        "query": item["title"],
        "id": item["id"],
        "content_type": item["type"],
        "mode": "url"
    }
    
    # For series, we need season/episode
    if item["type"] in ["series", "anime"]:
        params["season"] = 1
        params["episode"] = 1
        
    res = requests.post(stream_url, params=params)
    
    if res.status_code == 200:
        result = res.json()
        print("Success!")
        print(f"Status: {result.get('status')}")
        print(f"URL: {result.get('url')}")
        print(f"Title: {result.get('title')}")
    else:
        print(f"Stream request failed: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    test_stream_url_mode()
