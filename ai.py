"""
AI Integration Module - Mental Health Support with RAG
"""

# Force CPU-only mode
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import random
import logging
from typing import Optional

# Set up logging
logging.basicConfig(filename='ai_debug.log', level=logging.DEBUG)

# Import Hugging Face AI
from hf_ai import call_huggingface_api

# Import RAG
from rag import get_rag_context, RAG_ENABLED

# Fallback responses (when AI API is unavailable)
FALLBACK_RESPONSES = {
    'anxiety': [
        "I hear that you're feeling anxious. That must be really difficult. Would you like to try a breathing exercise together?",
        "Anxiety can feel overwhelming. You're not alone. Sometimes grounding yourself helps - can you name 5 things you see right now?",
    ],
    'sad': [
        "I'm sorry you're feeling this way. Your feelings are valid. Is there something specific weighing on you?",
        "It sounds like you're going through a tough time. I'm here to listen without judgment.",
    ],
    'stress': [
        "Stress can be really overwhelming. You're doing the best you can. What's one small thing you could do today for yourself?",
        "I hear that you're under a lot of pressure. Have you been able to take any breaks today?",
    ],
    'lonely': [
        "Feeling lonely is really painful. You're not alone in feeling this way. Is there someone you trust you could connect with?",
        "Loneliness can feel so heavy. Thank you for sharing this with me. I'm here for you.",
    ],
    'general': [
        "Thank you for sharing that with me. I'm here to listen. How are you feeling right now?",
        "I hear you. That sounds challenging. Would you like to talk more about what's on your mind?",
        "Your feelings matter. I'm here to support you.",
    ]
}


def is_relevant_topic(message: str) -> bool:
    """
    Check if the message is related to mental health or therapy.
    """
    if not message:
        return False
        
    message_lower = message.lower().strip()
    logging.debug(f"Checking relevance for: '{message_lower}'")
    
    # Positive keywords (Mental Health & Therapy Domain)
    RELEVANT_KEYWORDS = [
        'anxious', 'anxiety', 'sad', 'depression', 'depressed', 'stress', 'stressful',
        'therapy', 'therapist', 'counselor', 'psychologist', 'mental', 'health',
        'bipolar', 'ocd', 'trauma', 'ptsd', 'panic', 'nervous', 'scared', 'fear',
        'burnout', 'overwhelmed', 'lonely', 'loneliness', 'suicide', 'self-harm',
        'feeling', 'mood', 'emotion', 'help', 'support', 'listen', 'crying', 'hopeless',
        'peace', 'calm', 'breathing', 'meditation', 'grounding', 'mindfulness',
        'sleep', 'insomnia', 'worry', 'worried', 'struggling', 'pain', 'hurting',
        'relationship', 'family', 'friend', 'social', 'confidence', 'self-esteem',
        'suicide', 'kill', 'die', 'end it'
    ]
    
    # 1. Direct Keyword Check
    for word in RELEVANT_KEYWORDS:
        if word in message_lower:
            logging.debug(f"Relevance match: {word}")
            return True
    
    # 2. Check for emotional intensity (short messages)
    if len(message_lower.split()) <= 3:
        logging.debug("Relevance: short message allowed")
        return True

    # 3. Pattern check for common out-of-domain traps
    IRRELEVANT_PATTERNS = [
        'what is', 'who is', 'how to build', 'how to code', 'recipe', 'sports', 
        'news', 'current events', 'math', 'calculator', 'joke', 'weather'
    ]
    
    if any(pattern in message_lower for pattern in IRRELEVANT_PATTERNS):
        logging.debug("Relevance: irrelevant pattern match")
        return False
        
    # By default, for a mental health chatbot, we assume longer messages not matching irrelevant patterns are okay
    logging.debug("Relevance: default allowed")
    return True


def get_ai_response(user_message: str) -> str:
    """
    Generate empathetic AI response to user message
    """
    # Step 0: Topic Guardrail
    if not is_relevant_topic(user_message):
        return ("I'm here to support your mental health and emotional well-being. "
                "I focus on therapy, stress management, and empathetic listening. "
                "I'm unable to assist with general knowledge or off-topic queries, but I'm all ears if you'd like to talk about how you're feeling.")
    
    # Step 1: Try Hugging Face API with RAG
    api_response = call_huggingface_with_rag(user_message)
    if api_response:
        return api_response
    
    # Step 2: Fallback to pattern-based responses
    return get_fallback_response(user_message)


def call_huggingface_with_rag(user_message: str) -> Optional[str]:
    """
    Call Hugging Face API with RAG-augmented context
    """
    try:
        # Get RAG context if enabled
        context = ""
        if RAG_ENABLED:
            context = get_rag_context(user_message)
        
        # Call Hugging Face API
        response = call_huggingface_api(user_message, context=context)
        return response
        
    except Exception as e:
        logging.error(f"Error in hf_rag call: {e}")
        return None


def get_fallback_response(user_message: str) -> str:
    """
    Get pattern-based fallback response
    """
    message_lower = user_message.lower()
    
    # Detect emotional context
    if any(word in message_lower for word in ['anxious', 'anxiety', 'worried', 'nervous', 'panic']):
        category = 'anxiety'
    elif any(word in message_lower for word in ['sad', 'depressed', 'down', 'unhappy', 'crying']):
        category = 'sad'
    elif any(word in message_lower for word in ['stress', 'stressed', 'overwhelmed', 'pressure']):
        category = 'stress'
    elif any(word in message_lower for word in ['lonely', 'alone', 'isolated']):
        category = 'lonely'
    else:
        category = 'general'
    
    return random.choice(FALLBACK_RESPONSES[category])

def get_coping_strategy(strategy_type):
    """
    Return detailed coping strategy instructions
    """
    strategies = {
        'breathing': """**4-7-8 Breathing Exercise**\n\n1. Breathe in for 4s\n2. Hold for 7s\n3. Exhale for 8s""",
        'grounding': """**5-4-3-2-1 Grounding**\n\nName 5 things you see, 4 you can touch...""",
    }
    return strategies.get(strategy_type, strategies['breathing'])
