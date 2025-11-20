import sys
import os
import traceback

print("Attempting to import backend.main...")
try:
    from backend.main import app
    print("Import successful.")
except Exception:
    traceback.print_exc()
    sys.exit(1)

print("Attempting to run uvicorn...")
try:
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
except Exception:
    traceback.print_exc()
    sys.exit(1)
