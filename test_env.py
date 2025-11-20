print("Hello World")
import sys
print(sys.version)
try:
    import moviebox_api
    print("moviebox_api imported")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
