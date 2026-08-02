import requests
import json
import sseclient
import sys
import threading
import uvicorn
import time
from api import app

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="error")

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(2) # Wait for server to start

url = "http://localhost:8001/api/execute"
goal = "What is today's date? Just run the date command."
print(f"Goal: {goal}")

try:
    response = requests.post(url, json={"goal": goal})
    print(f"Execute response: {response.status_code} {response.text}")

    if response.status_code == 200:
        exec_id = response.json()["exec_id"]
        stream_url = f"http://localhost:8001/api/stream/{exec_id}"
        
        response = requests.get(stream_url, stream=True)
        client = sseclient.SSEClient(response)
        for event in client.events():
            print(f"Event: {event.data}")
except Exception as e:
    print(f"Error: {e}")
