"""
Quick test to check if chat endpoint is working with AI
"""
import requests
import json

# Test the chat endpoint
url = "http://localhost:5000/chat"
headers = {"Content-Type": "application/json"}
data = {"message": "hello, how are you?"}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
