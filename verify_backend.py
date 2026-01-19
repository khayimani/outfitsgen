import subprocess
import time
import requests
import os
import signal
import sys

def verify_backend():
    print("Starting backend server...")
    # Start the backend server
    # Use venv uvicorn
    uvicorn_path = "../venv/bin/uvicorn"
    if not os.path.exists(uvicorn_path):
        # Fallback if running from a different context or if venv structure is different
        uvicorn_path = "uvicorn"

    process = subprocess.Popen(
        [uvicorn_path, "main:app", "--port", "8000"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    try:
        # Wait for server to start
        print("Waiting for server to be healthy...")
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/")
                if response.status_code == 200:
                    print("Server is healthy!")
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        else:
            print("Failed to connect to server.")
            return False

        # Create a dummy image file
        print("Creating dummy image...")
        with open("test_image.jpg", "wb") as f:
            f.write(os.urandom(1024)) # 1KB of random data

        # Test /ingest endpoint
        print("Testing /ingest endpoint...")
        with open("test_image.jpg", "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = requests.post("http://localhost:8000/ingest", files=files)

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and "item_id" in data:
                print("Backend verification SUCCESS!")
                return True
            else:
                print("Backend verification FAILED: Invalid response format")
                return False
        else:
            print("Backend verification FAILED: Non-200 status code")
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        # Cleanup
        print("Cleaning up...")
        if os.path.exists("test_image.jpg"):
            os.remove("test_image.jpg")
        
        # Kill the process group
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait()

if __name__ == "__main__":
    success = verify_backend()
    sys.exit(0 if success else 1)
