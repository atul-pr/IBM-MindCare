"""Test AI module directly"""
from ai import get_ai_response

print("Testing AI module...")
print("=" * 60)

# Test 1: Normal conversation
print("\nTest 1: Normal conversation")
response = get_ai_response("I'm feeling anxious about work")
print(f"Response: {response[:200]}...")

# Test 2: Another message
print("\n\nTest 2: Stress message")
response = get_ai_response("I'm so stressed")
print(f"Response: {response[:200]}...")

print("\n" + "=" * 60)
print("✅ AI module test complete!")
