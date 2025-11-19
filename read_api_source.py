import os
import moviebox_api

path = os.path.dirname(moviebox_api.__file__)
download_file = os.path.join(path, "download.py")

try:
    with open(download_file, "r", encoding="utf-8") as f:
        content = f.read()

    with open("api_download_source.txt", "w", encoding="utf-8") as log:
        log.write(content)
    print("Read success")
except Exception as e:
    print(f"Error: {e}")
