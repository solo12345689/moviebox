import requests
import sys

API_URL = "http://localhost:8000/api"
LOG_FILE = "verify_result.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def test_stream_url_mode():
    log("Testing /stream with mode='url'...")
    
    try:
        # 1. Search
        log("Searching for 'Naruto'...")
        search_res = requests.get(f"{API_URL}/search", params={"query": "Naruto", "content_type": "anime"})
        if search_res.status_code != 200:
            log(f"Search failed: {search_res.text}")
            return
            
        data = search_res.json()
        if not data.get("results"):
            log("No results found")
            return
            
        item = data["results"][0]
        log(f"Found item: {item['title']} (ID: {item['id']})")
        
        # 2. Request Stream URL
        log("Requesting stream URL...")
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
            log("Success!")
            log(f"Status: {result.get('status')}")
            log(f"URL: {result.get('url')}")
            log(f"Title: {result.get('title')}")
        else:
            log(f"Stream request failed: {res.status_code}")
            log(res.text)
            
    except Exception as e:
        log(f"Exception: {e}")

if __name__ == "__main__":
    # Clear log
    with open(LOG_FILE, "w") as f:
        f.write("")
    test_stream_url_mode()
