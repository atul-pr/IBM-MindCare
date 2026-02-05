import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL = "google/flan-t5-base"

URL = f"https://router.huggingface.co/hf-inference/models/{MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "inputs": "Explain anxiety in simple and supportive language.",
    "parameters": {
        "max_new_tokens": 120,
        "temperature": 0.7
    }
}

print(f"API Key: {HF_API_KEY[:15]}...")
print(f"URL: {URL}")
print("Calling API...")

response = requests.post(URL, headers=HEADERS, json=payload, timeout=60)

print("Status:", response.status_code)
print("Response:", response.text)
