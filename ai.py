"""
AI Integration Module - Mental Health Support with RAG
Uses Hugging Face Inference API + RAG for empathetic, grounded responses

ARCHITECTURE:
1. Crisis Detection (FIRST - safety override)
2. RAG Context Retrieval (if enabled)
3. Hugging Face AI (with context)
4. Fallback Responses (if API fails)

WHY THIS APPROACH:
- Safety first: Crisis detection runs before AI
- Grounded responses: RAG provides verified information
- Reliable: Fallback ensures chatbot always responds
- Free: Hugging Face free tier has no quota limits
"""

import random
from typing import Optional

# Import Hugging Face AI
from hf_ai import call_huggingface_api

# Import RAG
from rag import get_rag_context, RAG_ENABLED

# Fallback responses (when AI API is unavailable)
FALLBACK_RESPONSES = {
    'anxiety': [
        "I hear that you're feeling anxious. That must be really difficult. Would you like to try a breathing exercise together? Breathe in for 4 counts, hold for 7, and exhale for 8. This can help calm your nervous system.",
        "Anxiety can feel overwhelming. You're not alone in this. Sometimes it helps to ground yourself - can you name 5 things you can see around you right now? This can help bring you back to the present moment.",
    ],
    'sad': [
        "I'm sorry you're feeling this way. Your feelings are valid, and it's okay to not be okay sometimes. Is there something specific that's been weighing on you?",
        "It sounds like you're going through a tough time. Would it help to talk about what's making you feel sad? I'm here to listen without judgment.",
    ],
    'stress': [
        "Stress can be really overwhelming. You're doing the best you can. Sometimes breaking things into smaller steps can help - what's one small thing you could do today to take care of yourself?",
        "I hear that you're under a lot of pressure. That's exhausting. Have you been able to take any breaks today? Even 5 minutes of deep breathing can make a difference.",
    ],
    'lonely': [
        "Feeling lonely is really painful, and I'm glad you reached out. You're not alone in feeling this way. Is there someone you trust that you could connect with, even just a text or call?",
        "Loneliness can feel so heavy. Thank you for sharing this with me. Sometimes small connections help - have you considered joining a community group or online forum about something you enjoy?",
    ],
    'general': [
        "Thank you for sharing that with me. I'm here to listen. How are you feeling right now?",
        "I hear you. That sounds challenging. Would you like to talk more about what's on your mind?",
        "Your feelings matter. I'm here to support you. What would be most helpful for you right now?",
    ]
}


def get_ai_response(user_message: str) -> str:
    """
    Generate empathetic AI response to user message
    
    FLOW:
    1. Try Hugging Face API with RAG context
    2. If API fails, use fallback responses
    
    Args:
        user_message (str): User's message
        
    Returns:
        str: Bot's empathetic response
    """
    
    # Step 1: Try Hugging Face API with RAG
    api_response = call_huggingface_with_rag(user_message)
    if api_response:
        return api_response
    
    # Step 2: Fallback to pattern-based responses
    return get_fallback_response(user_message)


def call_huggingface_with_rag(user_message: str) -> Optional[str]:
    """
    Call Hugging Face API with RAG-augmented context
    
    HOW RAG WORKS:
    1. User message is converted to embedding
    2. Similar chunks retrieved from FAISS vector store
    3. Retrieved context added to prompt
    4. AI generates response grounded in retrieved information
    
    Args:
        user_message (str): User's message
        
    Returns:
        Optional[str]: AI response or None if API fails
    """
    try:
        # Get RAG context if enabled
        context = ""
        if RAG_ENABLED:
            print("DEBUG: Retrieving RAG context...")
            context = get_rag_context(user_message)
            if context:
                print(f"DEBUG: Retrieved {len(context)} chars of context")
            else:
                print("DEBUG: No relevant context found")
        
        # Call Hugging Face API
        print(f"DEBUG: Calling Hugging Face API (RAG: {bool(context)})...")
        response = call_huggingface_api(user_message, context=context)
        
        if response:
            print("DEBUG: HF API call successful!")
            return response
        
        print("DEBUG: HF API returned no response")
        return None
        
    except Exception as e:
        print(f"DEBUG: Error in HF+RAG call: {e}")
        return None


def get_fallback_response(user_message: str) -> str:
    """
    Get pattern-based fallback response
    
    Used when Hugging Face API is unavailable
    
    Args:
        user_message (str): User's message
        
    Returns:
        str: Fallback response
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


# ============================================================================
# COPING STRATEGIES (kept from original)
# ============================================================================

def get_coping_strategy(strategy_type):
    """
    Return detailed coping strategy instructions
    
    Args:
        strategy_type (str): Type of coping strategy
        
    Returns:
        str: Formatted coping strategy
    """
    strategies = {
        'breathing': """**4-7-8 Breathing Exercise**

Let's try this together:
1. Breathe in through your nose for 4 counts
2. Hold your breath for 7 counts
3. Exhale slowly through your mouth for 8 counts
4. Repeat 3-4 times

This activates your body's relaxation response. How do you feel?""",
        
        'grounding': """**5-4-3-2-1 Grounding Technique**

This helps when you feel overwhelmed:
- Name 5 things you can see
- Name 4 things you can touch
- Name 3 things you can hear
- Name 2 things you can smell
- Name 1 thing you can taste

This brings you back to the present moment.""",
        
        'journaling': """**Journaling Prompt**

Try writing about:
- What am I feeling right now?
- What triggered this feeling?
- What do I need in this moment?
- What's one small thing I can do for myself?

No need to write perfectly - just let it flow.""",
        
        'movement': """**Gentle Movement**

Physical activity can help shift your mood:
- Take a 5-minute walk
- Do some gentle stretches
- Dance to your favorite song
- Do 10 jumping jacks

Movement releases endorphins and can help process emotions."""
    }
    
    return strategies.get(strategy_type, strategies['breathing'])
