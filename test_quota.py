"""Test if Gemini API is still working or if quota is exceeded"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

print("=" * 60)
print("GEMINI API QUOTA TEST")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

if not api_key:
    print("\n❌ No API key found")
    exit(1)

print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")

try:
    genai.configure(api_key=api_key)
    print("✓ API configured")
    
    # Try to create model and generate content
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    print("✓ Model created: models/gemini-2.0-flash")
    
    print("\nAttempting to generate content...")
    response = model.generate_content(
        "Say 'API is working' in one sentence",
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=50,
        )
    )
    
    if response and response.text:
        print("\n" + "=" * 60)
        print("✅ SUCCESS - API IS WORKING!")
        print("=" * 60)
        print(f"\nResponse: {response.text}")
        print("\n✓ No quota issues detected")
    else:
        print("\n❌ Response received but no text")
        
except Exception as e:
    error_msg = str(e)
    print("\n" + "=" * 60)
    print("❌ ERROR DETECTED")
    print("=" * 60)
    print(f"\nError: {error_msg}")
    
    # Check for specific quota errors
    if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
        print("\n🚨 QUOTA/RATE LIMIT EXCEEDED!")
        print("\nPossible causes:")
        print("- Free tier daily quota exceeded")
        print("- Too many requests per minute")
        print("- API key needs billing enabled")
        print("\nSolutions:")
        print("1. Wait 24 hours for quota reset")
        print("2. Enable billing on Google Cloud Console")
        print("3. Use a different API key")
    elif "404" in error_msg:
        print("\n⚠️ Model not found - may need different model name")
    elif "403" in error_msg or "permission" in error_msg.lower():
        print("\n⚠️ Permission denied - API key may be invalid or restricted")
    else:
        print("\n⚠️ Unknown error - see details above")
    
    print("\n" + "=" * 60)
    
    # Print full traceback for debugging
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
