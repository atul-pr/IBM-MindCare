"""Simple quota check"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

print("TESTING GEMINI API")
print("=" * 50)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    response = model.generate_content("Say hello")
    
    print("✅ API IS WORKING!")
    print(f"Response: {response.text}")
    
except Exception as e:
    error_str = str(e)
    print("❌ API ERROR!")
    print(f"Error: {error_str}")
    
    if "429" in error_str:
        print("\n🚨 RATE LIMIT EXCEEDED!")
        print("You've made too many requests.")
        print("Wait a few minutes and try again.")
    elif "quota" in error_str.lower():
        print("\n🚨 QUOTA EXCEEDED!")
        print("Daily quota limit reached.")
        print("Wait 24 hours or enable billing.")
    elif "404" in error_str:
        print("\n⚠️ Model not found")
    else:
        print("\n⚠️ Unknown error")
