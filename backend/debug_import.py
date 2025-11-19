import sys
import threading
import time

def timeout():
    print("Timeout reached, exiting")
    sys.exit(1)

timer = threading.Timer(5.0, timeout)
timer.start()

print("Starting import...")
try:
    import moviebox_api
    print("Import successful")
    print(f"File: {moviebox_api.__file__}")
except Exception as e:
    print(f"Import failed: {e}")
finally:
    timer.cancel()
