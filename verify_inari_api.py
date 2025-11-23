import requests
import json
import sys

API_URL = "http://localhost:8000/api"

def log(msg):
    with open("verify_inari_api.log", "a") as f:
        f.write(str(msg) + "\n")
    print(msg)

def verify():
    query = "Inari Kon Kon Koi Iroha"
    log(f"Searching for: {query}")
    
    try:
        # 1. Search
        response = requests.get(f"{API_URL}/search", params={"query": query, "content_type": "all"})
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                item = results[0]
                log(f"Found item: {item['title']} (ID: {item['id']})")
                
                # 2. Get Details
                log("Fetching details...")
                # The ID from search might need encoding or is already suitable. 
                # Based on previous debugging, the ID is passed as query param 'id' to details endpoint?
                # Wait, looking at api.py: @router.get("/details/{path}")
                # And it takes 'id' as query param.
                
                # item['id'] from search result is the path? No.
                # In search results:
                # 'id': item.detailPath,
                # 'subjectId': item.subjectId
                
                # The frontend calls: /api/details/{id}?id={subjectId}&content_type={type}
                # where {id} is the detailPath.
                
                detail_path = item['id'] # This is actually detailPath in the mapped response
                subject_id = item.get('subjectId') # We might not have mapped this in search results?
                # Let's check what search returns.
                
                # In api.py search endpoint:
                # "id": item.detailPath,
                # "subjectId": item.subjectId,
                
                params = {
                    "id": subject_id,
                    "content_type": item['type']
                }
                
                log(f"Requesting details for path: {detail_path} with params: {params}")
                details_res = requests.get(f"{API_URL}/details/{detail_path}", params=params)
                
                if details_res.status_code == 200:
                    details = details_res.json()
                    log("Successfully got details!")
                    seasons = details.get('seasons', [])
                    log(f"Seasons found: {len(seasons)}")
                    if seasons:
                        log(f"First season: {seasons[0]}")
                else:
                    log(f"Details failed: {details_res.status_code} - {details_res.text}")
            else:
                log("No results found")
        else:
            log(f"Search failed: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"Exception: {e}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    # Clear log
    with open("verify_inari_api.log", "w") as f:
        f.write("")
    verify()
