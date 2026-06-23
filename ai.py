"""
AI Integration Module - Mental Health Support with RAG

Provider waterfall (fastest → most reliable):
  1. Groq API     — ~0.3-1s,  14,400 req/day FREE  ← PRIMARY
  2. HuggingFace  — ~5-25s,   ~1,000 req/day FREE  ← FALLBACK
  3. Pattern-based — instant,  unlimited             ← LAST RESORT
"""

# Force CPU-only mode
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import random
import logging
from typing import Optional

# Log to stdout — Railway captures stdout/stderr in its dashboard
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import AI providers
from groq_ai import call_groq_api
from hf_ai import call_huggingface_api

# Import RAG
from rag import get_rag_context, RAG_ENABLED

# ── Fallback responses (when ALL APIs are unavailable) ────────────────────────
FALLBACK_RESPONSES = {
    'anxiety': [
        "I hear that you're feeling anxious. That must be really difficult. Would you like to try a breathing exercise together?",
        "Anxiety can feel overwhelming. You're not alone. Sometimes grounding yourself helps — can you name 5 things you see right now?",
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
        'kill', 'die', 'end it', 'give up'
    ]

    # 1. Direct keyword check
    for word in RELEVANT_KEYWORDS:
        if word in message_lower:
            return True

    # 2. Short messages — assume emotional (e.g. "Hey", "I'm not okay")
    if len(message_lower.split()) <= 3:
        return True

    # 3. Filter obvious off-topic patterns
    IRRELEVANT_PATTERNS = [
        'how to build', 'how to code', 'recipe', 'sports score',
        'news', 'current events', 'math problem', 'calculator', 'weather forecast'
    ]
    if any(pattern in message_lower for pattern in IRRELEVANT_PATTERNS):
        return False

    # Default: allow — mental health conversations are wide-ranging
    return True


def _get_rag_context(user_message: str) -> str:
    """Safely retrieve RAG context; returns empty string on any error."""
    try:
        if RAG_ENABLED:
            return get_rag_context(user_message)
    except Exception as e:
        logger.warning(f"RAG context failed: {e}")
    return ""


def get_ai_response(user_message: str, history: list = None) -> str:
    """
    Generate empathetic AI response using provider waterfall:
      Groq → HuggingFace → Pattern fallback

    Args:
        user_message: Current user message
        history: List of prior messages [{'role': 'user'|'assistant', 'content': '...'}]
    """
    if history is None:
        history = []

    # Step 0: Topic guardrail
    if not is_relevant_topic(user_message):
        return (
            "I'm here to support your mental health and emotional well-being. "
            "I focus on therapy, stress management, and empathetic listening. "
            "I'm unable to assist with general knowledge queries, but I'm all ears "
            "if you'd like to talk about how you're feeling. 💙"
        )

    # Get RAG context once — shared across all providers
    context = _get_rag_context(user_message)

    # ── Step 1: Groq (ultra-fast, ~0.3-1s) ───────────────────────────────
    try:
        groq_response = call_groq_api(user_message, context=context, history=history)
        if groq_response:
            logger.info("[AI] Provider: Groq ✅")
            return groq_response
    except Exception as e:
        logger.warning(f"[AI] Groq exception: {e}")

    # ── Step 2: HuggingFace (reliable backup, ~5-25s) ─────────────────────
    try:
        hf_response = call_huggingface_api(user_message, context=context, history=history)
        if hf_response:
            logger.info("[AI] Provider: HuggingFace ✅")
            return hf_response
    except Exception as e:
        logger.warning(f"[AI] HuggingFace exception: {e}")

    # ── Step 3: Pattern-based fallback (instant, no API needed) ──────────
    logger.warning("[AI] All APIs failed — using pattern fallback")
    return get_fallback_response(user_message)


def get_fallback_response(user_message: str) -> str:
    """Pattern-based fallback response when all APIs are unavailable."""
    message_lower = user_message.lower()

    if any(w in message_lower for w in ['anxious', 'anxiety', 'worried', 'nervous', 'panic']):
        category = 'anxiety'
    elif any(w in message_lower for w in ['sad', 'depressed', 'down', 'unhappy', 'crying']):
        category = 'sad'
    elif any(w in message_lower for w in ['stress', 'stressed', 'overwhelmed', 'pressure']):
        category = 'stress'
    elif any(w in message_lower for w in ['lonely', 'alone', 'isolated']):
        category = 'lonely'
    else:
        category = 'general'

    return random.choice(FALLBACK_RESPONSES[category])


def get_coping_strategy(strategy_type: str) -> str:
    """Return detailed coping strategy instructions."""
    strategies = {
        'breathing': "**4-7-8 Breathing Exercise**\n\n1. Breathe in for 4s\n2. Hold for 7s\n3. Exhale for 8s\n\nRepeat 3-4 times.",
        'grounding': "**5-4-3-2-1 Grounding**\n\nName:\n- 5 things you see\n- 4 you can touch\n- 3 you can hear\n- 2 you can smell\n- 1 you can taste",
    }
    return strategies.get(strategy_type, strategies['breathing'])
