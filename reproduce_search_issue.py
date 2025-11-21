import requests
import time
import json
import sys

API_URL = "http://localhost:8000/api/search"

def log(msg):
    with open("reproduce_log.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def test_search(query, attempt):
    log(f"\n--- Attempt {attempt}: Searching for '{query}' ---")
    start_time = time.time()
    try:
        response = requests.get(API_URL, params={"query": query, "content_type": "all"})
        duration = time.time() - start_time
        log(f"Status Code: {response.status_code}")
        log(f"Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            log(f"Results count: {len(results)}")
            if len(results) > 0:
                log(f"First result: {results[0]['title']} ({results[0]['type']})")
            else:
                log("No results found.")
        else:
            log(f"Error: {response.text}")
            
    except Exception as e:
        log(f"Exception: {e}")

if __name__ == "__main__":
    # Clear log
    with open("reproduce_log.txt", "w") as f:
        f.write("Starting test...\n")
        
    log("Testing search consistency...")
    
    # First attempt
    test_search("Naruto", 1)
    
    # Wait a second
    time.sleep(1)
    
    # Second attempt
    test_search("Naruto", 2)
