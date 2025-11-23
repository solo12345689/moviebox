import requests
import json
import sys

API_URL = "http://localhost:8000/api/search"

def log(msg):
    with open("verify_anime_movie.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

def verify():
    query = "Naruto the Movie: Ninja Clash in the Land of Snow"
    log(f"Searching for: {query}")
    
    try:
        response = requests.get(API_URL, params={"query": query, "content_type": "all"})
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                item = results[0]
                log(f"Title: {item['title']}")
                log(f"Type: {item['type']}")
                
                if item['type'] == 'anime_movie':
                    log("SUCCESS: Item identified as 'anime_movie'")
                elif item['type'] == 'movie':
                    log("SUCCESS: Item identified as 'movie'")
                else:
                    log(f"FAILURE: Item identified as '{item['type']}'")
            else:
                log("No results found")
        else:
            log(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"Exception: {e}")

if __name__ == "__main__":
    # Clear log
    with open("verify_anime_movie.log", "w") as f:
        f.write("")
    verify()
