import moviebox_api
import sys
import os

try:
    loc = os.path.dirname(moviebox_api.__file__)
    with open("api_loc.txt", "w", encoding="utf-8") as f:
        f.write(loc)
    print(f"Location written: {loc}")
except Exception as e:
    with open("api_loc.txt", "w", encoding="utf-8") as f:
        f.write(f"Error: {e}")
    print(f"Error: {e}")
