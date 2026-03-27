import uvicorn
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.main import app

if __name__ == "__main__":
    print("Starting uvicorn direct...")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
    except Exception as e:
        print(f"FAILED TO START: {e}")
