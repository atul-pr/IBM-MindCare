"""Test API key validity and list available models"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

print("=" * 60)
print("GEMINI API KEY VALIDATION TEST")
print("=" * 60)
print(f"\nAPI Key found: {api_key[:10]}...{api_key[-4:]}")
print(f"API Key length: {len(api_key)}")

if not api_key or api_key == 'your-api-key-here':
    print("\n❌ FAILED: No valid API key found")
    exit(1)

try:
    genai.configure(api_key=api_key)
    print("\n✓ API configured successfully")
    
    print("\n" + "=" * 60)
    print("LISTING AVAILABLE MODELS")
    print("=" * 60)
    
    models = list(genai.list_models())
    
    if not models:
        print("\n❌ No models found - API key might be invalid")
    else:
        print(f"\n✓ Found {len(models)} total models")
        print("\nModels that support generateContent:")
        print("-" * 60)
        
        content_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                content_models.append(model)
                print(f"\n✓ {model.name}")
                print(f"  Display: {model.display_name}")
                print(f"  Description: {model.description[:80]}...")
        
        if not content_models:
            print("\n❌ No models support generateContent")
        else:
            print(f"\n\n{'=' * 60}")
            print(f"TESTING WITH FIRST AVAILABLE MODEL")
            print("=" * 60)
            
            test_model = content_models[0]
            print(f"\nUsing: {test_model.name}")
            
            model = genai.GenerativeModel(test_model.name)
            response = model.generate_content("Say hello in one sentence")
            
            if response and response.text:
                print("\n✅ SUCCESS! API is working!")
                print(f"\nResponse: {response.text}")
            else:
                print("\n❌ FAILED: No response text")
                
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
