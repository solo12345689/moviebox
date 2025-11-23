import uvicorn
import sys
import traceback

def run():
    try:
        print("Starting backend...")
        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception:
        with open("backend_error.log", "w") as f:
            f.write(traceback.format_exc())
        print("Backend failed to start.")
        traceback.print_exc()

if __name__ == "__main__":
    run()
