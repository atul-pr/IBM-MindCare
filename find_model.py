"""Quick test to find working model"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

genai.configure(api_key=api_key)

# Get first model that supports generateContent
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Working model: {model.name}")
        
        # Test it
        test_model = genai.GenerativeModel(model.name)
        response = test_model.generate_content("Say hello")
        print(f"Response: {response.text}")
        break
