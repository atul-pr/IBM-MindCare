"""
Hugging Face AI Module - Mental Health Support
Uses Hugging Face InferenceClient with CHAT API (correct task)
"""

import os
from typing import Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

# Hugging Face Configuration
HF_API_KEY = os.getenv('HF_API_KEY', '')
MODEL = "meta-llama/Llama-3.2-1B-Instruct"

# System prompt for mental health support
SYSTEM_PROMPT = """You are a compassionate mental health support chatbot for India. 
Be empathetic, warm, and supportive. Never diagnose or prescribe medication.
Keep responses under 100 words. Use simple, caring language."""


def call_huggingface_api(user_message: str, context: str = "") -> Optional[str]:
    """
    Call Hugging Face via InferenceClient CHAT API
    Zephyr model requires conversational/chat task, not text-generation
    """
    if not HF_API_KEY or HF_API_KEY == 'your-huggingface-api-key-here':
        print("DEBUG: No HF API key found, using fallback")
        return None
    
    try:
        print(f"DEBUG: Calling Hugging Face Chat API...")
        
        # Create client
        client = InferenceClient(
            model=MODEL,
            token=HF_API_KEY,
        )
        
        # Build system message with RAG context if available
        system_content = SYSTEM_PROMPT
        if context:
            system_content += f"\n\nRelevant information:\n{context[:300]}"
        
        # Create chat messages
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ]
        
        # Call CHAT API (not text_generation)
        response = client.chat.completions.create(
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        
        if response and response.choices:
            result = response.choices[0].message.content
            print("DEBUG: HF API call successful!")
            return result.strip()
        
        return None
            
    except Exception as e:
        print(f"DEBUG: HF API exception: {e}")
        return None


def test_hf_api():
    """Test function to verify HF API connectivity"""
    print("=" * 60)
    print("TESTING HUGGING FACE CHAT API")
    print("=" * 60)
    
    if not HF_API_KEY or HF_API_KEY == 'your-huggingface-api-key-here':
        print("\n❌ No API key configured")
        return False
    
    print(f"\nAPI Key: {HF_API_KEY[:10]}...{HF_API_KEY[-4:]}")
    print(f"Model: {MODEL}")
    
    test_message = "I'm feeling anxious"
    print(f"\nTest message: '{test_message}'")
    
    response = call_huggingface_api(test_message)
    
    if response:
        print("\n✅ SUCCESS!")
        print(f"\nResponse: {response}")
        return True
    else:
        print("\n❌ FAILED")
        return False


if __name__ == "__main__":
    test_hf_api()
