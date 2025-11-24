import sys
import os
import traceback

log_file = "debug_import_robust.log"

def log(msg):
    with open(log_file, "a") as f:
        f.write(msg + "\n")

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
