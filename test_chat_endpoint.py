"""Test chat endpoint directly"""
import requests
import json

# Test the chat endpoint
url = "http://localhost:5000/chat"

test_messages = [
    "I'm feeling anxious about my exams",
    "Can you help me with stress?",
    "Tell me about breathing exercises"
]

print("=" * 60)
print("TESTING CHAT ENDPOINT")
print("=" * 60)

for msg in test_messages:
    print(f"\n\nUser: {msg}")
    print("-" * 60)
    
    try:
        response = requests.post(
            url,
            json={"message": msg},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get('response', '')
            is_crisis = data.get('crisis', False)
            
            print(f"Status: ✅ Success")
            print(f"Crisis: {is_crisis}")
            print(f"Response length: {len(bot_response)} chars")
            print(f"Response: {bot_response[:300]}...")
        else:
            print(f"Status: ❌ Error {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
