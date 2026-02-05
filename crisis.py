"""
Crisis Detection Module - Rule-based safety layer
Detects suicidal ideation, self-harm, and extreme distress
"""

import re

# Crisis keyword patterns (case-insensitive)
SUICIDE_KEYWORDS = [
    'suicide', 'kill myself', 'end my life', 'want to die', 
    'better off dead', 'no reason to live', 'end it all',
    'take my own life', 'don\'t want to live'
]

SELF_HARM_KEYWORDS = [
    'hurt myself', 'cut myself', 'self harm', 'self-harm',
    'harm myself', 'injure myself', 'punish myself'
]

EXTREME_DISTRESS_KEYWORDS = [
    'can\'t go on', 'give up on life', 'no point living',
    'worthless', 'hopeless', 'nothing matters anymore',
    'everyone would be better without me', 'burden to everyone'
]

# Context exclusions (avoid false positives)
EXCLUSION_PATTERNS = [
    r'kill.*exam', r'kill.*test', r'die.*laughing',
    r'kill.*assignment', r'suicide.*mission'
]

def detect_crisis(message):
    """
    Detect crisis indicators in user message
    
    Args:
        message (str): User's message
        
    Returns:
        tuple: (is_crisis: bool, crisis_type: str)
    """
    message_lower = message.lower()
    
    # Check for false positive contexts first
    for pattern in EXCLUSION_PATTERNS:
        if re.search(pattern, message_lower):
            return False, None
    
    # Check for suicide indicators
    for keyword in SUICIDE_KEYWORDS:
        if keyword in message_lower:
            return True, 'suicide'
    
    # Check for self-harm indicators
    for keyword in SELF_HARM_KEYWORDS:
        if keyword in message_lower:
            return True, 'self_harm'
    
    # Check for extreme distress (multiple keywords = higher risk)
    distress_count = sum(1 for keyword in EXTREME_DISTRESS_KEYWORDS if keyword in message_lower)
    if distress_count >= 2:
        return True, 'extreme_distress'
    
    return False, None

def get_crisis_response(crisis_type):
    """
    Generate appropriate crisis response based on type
    
    Args:
        crisis_type (str): Type of crisis detected
        
    Returns:
        str: Crisis response message
    """
    base_message = """I'm really concerned about what you're sharing. Your safety is the most important thing right now.

🆘 **Please reach out to these helplines immediately:**

📞 **Kiran Mental Health Helpline**
   1800-599-0019 (24/7, Free)

📞 **AASRA**
   +91-9820466726 (24/7)

📞 **Sneha India Foundation**
   044-24640050 (24/7)

You don't have to face this alone. These trained counselors are ready to listen and help right now.

If you're in immediate danger, please:
- Call emergency services (112)
- Go to the nearest hospital emergency room
- Tell a trusted friend or family member

You matter, and there are people who want to help you through this."""

    if crisis_type == 'suicide':
        return base_message
    elif crisis_type == 'self_harm':
        return base_message.replace(
            "I'm really concerned about what you're sharing.",
            "I hear that you're thinking about hurting yourself, and I'm really concerned."
        )
    elif crisis_type == 'extreme_distress':
        return base_message.replace(
            "I'm really concerned about what you're sharing.",
            "I can hear how much pain you're in right now, and I'm concerned about your safety."
        )
    
    return base_message

def get_helpline_info():
    """
    Return formatted helpline information
    
    Returns:
        dict: Helpline contact information
    """
    return {
        'kiran': {
            'name': 'Kiran Mental Health Helpline',
            'number': '1800-599-0019',
            'availability': '24/7',
            'description': 'Government of India mental health helpline'
        },
        'aasra': {
            'name': 'AASRA',
            'number': '+91-9820466726',
            'availability': '24/7',
            'description': 'Suicide prevention helpline'
        },
        'sneha': {
            'name': 'Sneha India Foundation',
            'number': '044-24640050',
            'availability': '24/7',
            'description': 'Emotional support and crisis intervention'
        },
        'vandrevala': {
            'name': 'Vandrevala Foundation',
            'number': '9999 666 555',
            'availability': '24/7',
            'description': 'Mental health support and counseling'
        }
    }
