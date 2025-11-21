import requests
import time

def log(msg):
    print(msg)
    with open('health_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

def check_health():
    with open('health_log.txt', 'w') as f:
        f.write("Starting health check...\n")

    url = "http://localhost:8001/"
    log(f"Checking {url}...")
    try:
        response = requests.get(url, timeout=5)
        log(f"Status Code: {response.status_code}")
        log(f"Response: {response.json()}")
    except Exception as e:
        log(f"Health check failed: {e}")

if __name__ == "__main__":
    check_health()
