from moviebox_api import DownloadTracker, Downloader
import inspect

def inspect_classes():
    print("--- DownloadTracker ---")
    try:
        print(help(DownloadTracker))
    except Exception as e:
        print(f"Error inspecting DownloadTracker: {e}")

    print("\n--- Downloader ---")
    try:
        print(help(Downloader))
    except Exception as e:
        print(f"Error inspecting Downloader: {e}")

if __name__ == "__main__":
    inspect_classes()
