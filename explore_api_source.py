import os
import moviebox_api

path = os.path.dirname(moviebox_api.__file__)
with open("api_dir_list.txt", "w", encoding="utf-8") as log:
    log.write(f"Listing {path}:\n")
    for f in os.listdir(path):
        log.write(f"{f}\n")

    download_path = os.path.join(path, "download")
    if os.path.exists(download_path):
        log.write(f"\nListing {download_path}:\n")
        for f in os.listdir(download_path):
            log.write(f"{f}\n")
