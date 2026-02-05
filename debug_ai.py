"""Debug AI response in detail"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Test the exact code path from ai.py
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

print("=" * 60)
print("DEBUGGING AI MODULE")
print("=" * 60)
print(f"\nAPI Key loaded: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
print(f"API Key length: {len(GEMINI_API_KEY)}")
print(f"API Key is empty: {not GEMINI_API_KEY}")

if not GEMINI_API_KEY:
    print("\n❌ PROBLEM: No API key found!")
    exit(1)

print("\n✓ API key exists")

try:
    print("\nConfiguring genai...")
    genai.configure(api_key=GEMINI_API_KEY)
    print("✓ Configured")
    
    print("\nCreating model: models/gemini-2.0-flash")
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    print("✓ Model created")
    
    user_message = "I'm feeling anxious"
    
    SYSTEM_PROMPT = """You are a compassionate mental health support chatbot. Be empathetic and supportive."""
    
    prompt = f"""{SYSTEM_PROMPT}

User: {user_message}

Respond as a compassionate mental health support chatbot. Keep your response under 100 words, warm and empathetic."""
    
    print(f"\nGenerating response for: '{user_message}'")
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=150,
        )
    )
    
    print(f"\n✓ Response received")
    print(f"Response has text: {bool(response.text)}")
    print(f"Response text length: {len(response.text) if response.text else 0}")
    
    if response and response.text:
        print("\n" + "=" * 60)
        print("✅ SUCCESS - GEMINI IS WORKING!")
        print("=" * 60)
        print(f"\nResponse: {response.text}")
    else:
        print("\n❌ FAILED: Response exists but no text")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
