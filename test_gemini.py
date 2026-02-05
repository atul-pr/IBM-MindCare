"""
Test script to verify Google Gemini API connectivity
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test if Gemini API is working"""
    
    print("=" * 60)
    print("GEMINI API CONNECTIVITY TEST")
    print("=" * 60)
    
    # Check if API key exists
    api_key = os.getenv('GEMINI_API_KEY', '')
    
    if not api_key:
        print("❌ FAILED: No API key found in .env file")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add: GEMINI_API_KEY=your-actual-api-key")
        print("3. Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    if api_key == 'your-api-key-here':
        print("❌ FAILED: API key is still the placeholder value")
        print("\nTo fix this:")
        print("1. Go to: https://makersuite.google.com/app/apikey")
        print("2. Create an API key")
        print("3. Replace 'your-api-key-here' in .env with your actual key")
        return False
    
    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("✓ API key configured successfully")
    except Exception as e:
        print(f"❌ FAILED to configure API: {e}")
        return False
    
    # Test API call
    try:
        print("\nTesting API call...")
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        response = model.generate_content(
            "Say 'Hello! The Gemini API is working perfectly.' in a friendly way.",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=50,
            )
        )
        
        if response and response.text:
            print("✓ API call successful!")
            print(f"\nAPI Response:\n{response.text}")
            print("\n" + "=" * 60)
            print("✅ SUCCESS: Gemini API is working correctly!")
            print("=" * 60)
            return True
        else:
            print("❌ FAILED: No response from API")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: API call error: {e}")
        print("\nPossible issues:")
        print("- Invalid API key")
        print("- API quota exceeded")
        print("- Network connectivity issues")
        print("- API service temporarily unavailable")
        return False

if __name__ == '__main__':
    test_gemini_api()
