"""
Multi-Model HF API Test
Tries different models to find one that is active and supported on the free tier.
"""
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

api_key = os.getenv('HF_API_KEY', '')

print("=" * 60)
print("MULTI-MODEL HF API TEST")
print("=" * 60)

models_to_try = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "meta-llama/Llama-3.2-1B-Instruct",
    "microsoft/Phi-3-mini-4k-instruct",
    "Qwen/Qwen2.5-1.5B-Instruct"
]

def test_model(model_name):
    print(f"\nTesting: {model_name}")
    try:
        client = InferenceClient(model=model_name, token=api_key)
        
        # Using chat completions as it's the most standard now
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=20
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"✅ SUCCESS! Response: {content.strip()}")
            return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}...")
    return False

working_model = None
for model in models_to_try:
    if test_model(model):
        working_model = model
        break

if working_model:
    print("\n" + "=" * 60)
    print(f"WINNER: {working_model}")
    print("=" * 60)
else:
    print("\n❌ No models worked. Please check your HF_API_KEY or network connection.")
