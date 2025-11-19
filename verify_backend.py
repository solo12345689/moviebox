import requests
import time
import sys

API_URL = "http://localhost:8000/api"

def log(msg):
    with open("verify_output_direct.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def test_api():
    log("Testing API...")
    try:
        # Test Root
        try:
            r = requests.get("http://localhost:8000/")
            log(f"Root: {r.status_code}")
        except Exception as e:
            log(f"Root request failed: {e}")
            return

        if r.status_code != 200:
            log("Root failed")
            return

        # Test Search
        log("Testing Search...")
        try:
            r = requests.get(f"{API_URL}/search?query=Inception")
            log(f"Search: {r.status_code}")
        except Exception as e:
            log(f"Search request failed: {e}")
            return

        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            log(f"Found {len(results)} results")
            if results:
                item = results[0]
                log(f"First item: {item['title']} ({item['id']})")
                
                # Test Details
                log("Testing Details...")
                try:
                    r = requests.get(f"{API_URL}/details/{item['id']}")
                    log(f"Details: {r.status_code}")
                    if r.status_code == 200:
                        details = r.json()
                        log(f"Details title: {details.get('title')}")
                    else:
                        log(f"Details failed: {r.text}")
                except Exception as e:
                    log(f"Details request failed: {e}")
                
                # Test Download
                log("Testing Download...")
                try:
                    r = requests.post(f"{API_URL}/download?query={item['title']}")
                    log(f"Download: {r.status_code}")
                except Exception as e:
                    log(f"Download request failed: {e}")

                # Test Stream
                log("Testing Stream...")
                try:
                    r = requests.post(f"{API_URL}/stream?query={item['title']}")
                    log(f"Stream: {r.status_code}")
                    if r.status_code == 500 and "mpv" in r.text:
                        log("Stream failed as expected (mpv missing or not found)")
                    elif r.status_code == 200:
                        log("Stream launched successfully")
                except Exception as e:
                    log(f"Stream request failed: {e}")

        else:
            log(f"Search failed: {r.text}")

    except Exception as e:
        log(f"Test failed with exception: {e}")

if __name__ == "__main__":
    # Clear file
    open("verify_output_direct.txt", "w").close()
    test_api()
