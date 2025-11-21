import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def log(msg):
    print(msg)
    with open('import_test_log.txt', 'a') as f:
        f.write(str(msg) + '\n')

try:
    with open('import_test_log.txt', 'w') as f:
        f.write("Starting import test...\n")
        
    log("Attempting to import backend.api...")
    from backend.api import session
    log("Session created successfully")
except Exception as e:
    log(f"Error importing backend.api: {e}")
    import traceback
    log(traceback.format_exc())
