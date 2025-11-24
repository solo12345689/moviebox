import sys
import os
import traceback

# Use absolute path for log file
log_file = r"c:\Users\akshi\.gemini\antigravity\scratch\moviebox_web_app\backend\debug_import_absolute.log"

def log(msg):
    try:
        with open(log_file, "a") as f:
            f.write(msg + "\n")
    except Exception as e:
        print(f"Failed to write to log: {e}")

try:
    log("Starting import test...")
    log(f"CWD: {os.getcwd()}")
    log(f"Files: {os.listdir('.')}")
    
    import main
    log("Successfully imported main")
except Exception as e:
    log(f"Error importing main: {e}")
    with open(log_file, "a") as f:
        traceback.print_exc(file=f)
