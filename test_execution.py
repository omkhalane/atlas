import requests
import json
import sseclient

url = "http://127.0.0.1:8000/api/execute"
response = requests.post(url, json={"goal": "solve 4sum on leetcode using python"})
print(f"Execute response: {response.status_code} {response.text}")

if response.status_code == 200:
    exec_id = response.json()["exec_id"]
    stream_url = f"http://127.0.0.1:8000/api/stream/{exec_id}"
    print(f"Streaming from {stream_url}...")
    
    response = requests.get(stream_url, stream=True)
    client = sseclient.SSEClient(response)
    for event in client.events():
        print(event.data)
