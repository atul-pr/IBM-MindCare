"""Simple Gemini API test with file output"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY', '')

with open('gemini_test_result.txt', 'w', encoding='utf-8') as f:
    f.write("GEMINI API TEST RESULTS\n")
    f.write("=" * 60 + "\n\n")
    
    if not api_key:
        f.write("FAILED: No API key found\n")
        print("FAILED: No API key found")
    elif api_key == 'your-api-key-here':
        f.write("FAILED: API key is placeholder\n")
        print("FAILED: API key is placeholder")
    else:
        f.write(f"API Key: {api_key[:10]}...{api_key[-4:]}\n\n")
        
        try:
            genai.configure(api_key=api_key)
            f.write("API configured successfully\n\n")
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Say hello in one sentence")
            
            if response and response.text:
                f.write("SUCCESS: API is working!\n\n")
                f.write(f"Response: {response.text}\n")
                print("SUCCESS: Gemini API is working!")
                print(f"Response: {response.text}")
            else:
                f.write("FAILED: No response\n")
                print("FAILED: No response")
        except Exception as e:
            f.write(f"FAILED: {str(e)}\n")
            print(f"FAILED: {str(e)}")

print("\nFull results saved to: gemini_test_result.txt")
