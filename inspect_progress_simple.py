import sys
try:
    from moviebox_api import DownloadTracker, Downloader
    print("Import successful")
    print("DownloadTracker attributes:", dir(DownloadTracker))
    print("Downloader attributes:", dir(Downloader))
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
