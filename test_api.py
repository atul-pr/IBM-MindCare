"""Final Gemini API test"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

print("=" * 60)
print("GEMINI API TEST")
print("=" * 60)

if not api_key or api_key == 'your-api-key-here':
    print("FAILED: No valid API key")
else:
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        genai.configure(api_key=api_key)
        print("Configured successfully")
        
        model = genai.GenerativeModel('gemini-1.5-pro')
        print("Testing API call...")
        
        response = model.generate_content("Say 'Hello! Gemini API is working!' in a friendly way.")
        
        if response and response.text:
            print("\n" + "=" * 60)
            print("SUCCESS: Gemini API is working!")
            print("=" * 60)
            print(f"\nResponse: {response.text}")
        else:
            print("FAILED: No response")
    except Exception as e:
        print(f"FAILED: {str(e)}")
