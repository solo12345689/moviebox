import socket
import requests

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

local_ip = get_local_ip()
print(f"Local IP: {local_ip}")

try:
    response = requests.get(f"http://{local_ip}:8000/api/health", timeout=2)
    print(f"Connection to http://{local_ip}:8000/api/health: {response.status_code}")
except Exception as e:
    print(f"Failed to connect to http://{local_ip}:8000/api/health: {e}")
