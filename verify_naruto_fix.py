import requests
import json

def log(msg):
    print(msg)
    with open('verify_fix_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

def verify_fix():
    with open('verify_fix_log.txt', 'w') as f:
        f.write("Starting verification...\n")

    url = "http://localhost:8000/api/search"
    params = {"query": "Naruto: Shippuden [Hindi] S1-S15"}
    
    log(f"Querying {url} with params: {params}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "results" not in data or not data["results"]:
            log("No results found")
            return

        target_item = None
        for item in data["results"]:
            if "Naruto: Shippuden" in item["title"]:
                target_item = item
                break
        
        if target_item:
            log(f"Found item: {target_item['title']}")
            log(f"Detected Type: {target_item['type']}")
            
            if target_item['type'] in ['series', 'anime']:
                log("SUCCESS: Item correctly identified as series/anime")
            else:
                log(f"FAILURE: Item still identified as {target_item['type']}")
        else:
            log("Target item not found in search results")

    except Exception as e:
        log(f"Error: {e}")

if __name__ == "__main__":
    verify_fix()
