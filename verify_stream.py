import requests
import json

def log(msg):
    print(msg)
    with open('verify_stream_result.txt', 'a') as f:
        f.write(str(msg) + '\n')

def verify_stream():
    with open('verify_stream_result.txt', 'w') as f:
        f.write("Starting stream verification...\n")

    # 1. Search for the item to get ID
    query = "Naruto SD: Rock Lee & His Ninja Pals"
    log(f"Searching for: {query}")
    
    search_res = requests.get("http://localhost:8000/api/search", params={"query": query, "content_type": "anime"})
    
    if search_res.status_code != 200:
        log(f"Search failed: {search_res.status_code}")
        return

    search_data = search_res.json()
    if not search_data.get("results"):
        log("No results found")
        return

    target_item = search_data["results"][0]
    log(f"Found item: {target_item['title']} (ID: {target_item['id']})")

    # 2. Request Stream
    log("Requesting stream...")
    stream_payload = {
        "query": target_item['title'],
        "id": target_item['id'],
        "content_type": "anime",
        "season": 1,
        "episode": 1
    }
    
    # Note: The endpoint expects query params, not JSON body for this implementation?
    # Let's check api.py signature. It uses query params by default in FastAPI if not specified as Body.
    # But wait, App.jsx sends POST. FastAPI defaults scalar types to query params even for POST unless Body() is used.
    # Let's try sending as query params first.
    
    stream_res = requests.post("http://localhost:8000/api/stream", params=stream_payload)
    
    if stream_res.status_code == 200:
        log("Stream request successful!")
        log(f"Response: {stream_res.json()}")
    else:
        log(f"Stream request failed: {stream_res.status_code}")
        log(f"Error: {stream_res.text}")

if __name__ == "__main__":
    try:
        verify_stream()
    except Exception as e:
        log(f"Error: {e}")
