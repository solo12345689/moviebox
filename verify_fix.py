import requests
import json

def log(msg):
    print(msg)
    with open('verification_result.txt', 'a') as f:
        f.write(str(msg) + '\n')

try:
    # Clear previous result
    with open('verification_result.txt', 'w') as f:
        f.write("Starting verification...\n")

    log("Testing search API for Naruto Hindi...")
    response = requests.get("http://localhost:8000/api/search", params={"query": "Naruto Hindi", "content_type": "anime"})
    
    if response.status_code == 200:
        data = response.json()
        log(f"Status: {response.status_code}")
        
        if "results" in data and len(data["results"]) > 0:
            item = data["results"][0]
            log(f"Found item: {item.get('title')}")
            
            # Now get details
            log(f"Fetching details for ID: {item.get('id')}")
            details_res = requests.get(f"http://localhost:8000/api/details/{item.get('id')}")
            
            if details_res.status_code == 200:
                details = details_res.json()
                seasons = details.get("seasons", [])
                log(f"Seasons found: {len(seasons)}")
                
                # Log full details keys for debugging
                log(f"Details keys: {details.keys()}")
                if 'seasons' not in details or len(details['seasons']) == 0:
                     log(f"Full details dump: {json.dumps(details, indent=2)}")

                if len(seasons) > 0:
                    log(f"First season: {seasons[0]}")
                    log("VERIFICATION SUCCESSFUL: Seasons data is present.")
                else:
                    log("VERIFICATION FAILED: No seasons data found.")
            else:
                log(f"Details API failed: {details_res.status_code}")
                log(details_res.text)
        else:
            log("No results found")
    else:
        log(f"Search API failed: {response.status_code}")
        log(response.text)

except Exception as e:
    log(f"Error: {e}")
