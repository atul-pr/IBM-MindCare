"""
Test Hugging Face + RAG Integration
This script tests the complete AI pipeline
"""

print("=" * 60)
print("TESTING HUGGING FACE + RAG INTEGRATION")
print("=" * 60)

# Test 1: RAG Context Retrieval
print("\n\n1. TESTING RAG CONTEXT RETRIEVAL")
print("-" * 60)

from rag import get_rag_context, RAG_ENABLED

if RAG_ENABLED:
    test_queries = [
        "I'm feeling anxious",
        "How do I manage stress?",
        "breathing exercises"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        context = get_rag_context(query)
        if context:
            print(f"✅ Retrieved context ({len(context)} chars)")
            print(f"Preview: {context[:150]}...")
        else:
            print("❌ No context retrieved")
else:
    print("⚠️ RAG is disabled")

# Test 2: Hugging Face API (if key is configured)
print("\n\n2. TESTING HUGGING FACE API")
print("-" * 60)

from hf_ai import call_huggingface_api
import os
from dotenv import load_dotenv

load_dotenv()
hf_key = os.getenv('HF_API_KEY', '')

if hf_key and hf_key != 'your-huggingface-api-key-here':
    print(f"API Key: {hf_key[:10]}...")
    
    test_message = "I'm feeling stressed"
    print(f"\nTest message: '{test_message}'")
    
    # Test without RAG
    print("\nCalling HF API (without RAG)...")
    response = call_huggingface_api(test_message)
    
    if response:
        print(f"✅ SUCCESS!")
        print(f"Response: {response[:200]}...")
    else:
        print("⚠️ API call failed (model may be loading, try again in 20 seconds)")
    
    # Test with RAG
    if RAG_ENABLED:
        print("\nCalling HF API (with RAG)...")
        context = get_rag_context(test_message)
        response_with_rag = call_huggingface_api(test_message, context=context)
        
        if response_with_rag:
            print(f"✅ SUCCESS with RAG!")
            print(f"Response: {response_with_rag[:200]}...")
        else:
            print("⚠️ API call failed")
else:
    print("⚠️ No HF API key configured")
    print("Add HF_API_KEY to .env file to test")

# Test 3: Full AI Pipeline
print("\n\n3. TESTING FULL AI PIPELINE (ai.py)")
print("-" * 60)

from ai import get_ai_response

test_messages = [
    "I'm feeling anxious about my exams",
    "Can you help me with stress?",
]

for msg in test_messages:
    print(f"\nUser: {msg}")
    response = get_ai_response(msg)
    print(f"Bot: {response[:150]}...")

print("\n\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

print("\n\nNEXT STEPS:")
print("1. Add your HF API key to .env file")
print("2. Get token from: https://huggingface.co/settings/tokens")
print("3. Restart Flask app: python app.py")
print("4. Test in browser: http://localhost:5000")
