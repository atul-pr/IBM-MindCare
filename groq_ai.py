"""
Groq AI Module - Ultra-fast inference for HealSpace Mental Health Chatbot
Groq uses custom LPU (Language Processing Unit) hardware — ~10-30x faster than HuggingFace.

Free tier limits (as of 2024):
  - llama-3.1-8b-instant:    14,400 req/day,  6,000 tokens/min  ← PRIMARY
  - llama-3.3-70b-versatile: 14,400 req/day,  6,000 tokens/min  ← HIGH QUALITY
  - llama3-8b-8192:          14,400 req/day, 30,000 tokens/min
  - gemma2-9b-it:            14,400 req/day, 15,000 tokens/min

Get a free API key at: https://console.groq.com
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Note: key is read dynamically inside call_groq_api() so hot-reload / late .env loading works

# System prompt — same as HF module for consistency
SYSTEM_PROMPT = (
    "You are HealSpace, a compassionate AI mental health support companion for India. "
    "Your role is to listen with empathy, validate feelings, and offer gentle evidence-based coping strategies. "
    "Tone: warm, non-judgmental, conversational. "
    "Rules: never diagnose, never prescribe medication, always encourage professional help for serious issues. "
    "Keep responses to 2-4 sentences (under 120 words). Use simple, caring language. "
    "If the user mentions crisis or self-harm, gently redirect to the Kiran helpline: 1800-599-0019."
)

# ---------------------------------------------------------------------------
# GROQ MODEL PRIORITY
# Ordered by: speed → quality → availability
# ---------------------------------------------------------------------------
GROQ_MODELS = [
    {
        "id": "llama-3.1-8b-instant",
        "note": "Primary — fastest (~0.3s), 8B, great for real-time chat",
        "max_tokens": 250,
    },
    {
        "id": "llama3-8b-8192",
        "note": "Fallback — slightly older but very reliable",
        "max_tokens": 250,
    },
    {
        "id": "gemma2-9b-it",
        "note": "Fallback — Google Gemma 9B, high quality",
        "max_tokens": 250,
    },
    {
        "id": "llama-3.3-70b-versatile",
        "note": "Last resort — 70B params, best quality, slightly slower (~1s)",
        "max_tokens": 300,
    },
]


def call_groq_api(user_message: str, context: str = "") -> Optional[str]:
    """
    Call Groq API for ultra-fast AI responses.
    Tries models in priority order; falls back to next on failure.

    Returns:
        str: AI response text, or None if all models fail.
    """
    # Read key dynamically so late-loaded .env values are always picked up
    api_key = os.getenv('GROQ_API_KEY', '').strip()

    if not api_key or api_key in ('', 'your-groq-api-key-here'):
        logger.warning("[Groq] GROQ_API_KEY not set — skipping Groq, falling back to HuggingFace")
        return None

    logger.info(f"[Groq] API key detected: {api_key[:8]}... — starting inference")

    try:
        from groq import Groq
    except ImportError:
        logger.warning("[Groq] 'groq' package not installed — run: pip install groq")
        return None

    # Enrich system prompt with RAG context if available
    system_content = SYSTEM_PROMPT
    if context:
        system_content += f"\n\nRelevant mental health context:\n{context[:400]}"

    client = Groq(api_key=api_key)

    for model_cfg in GROQ_MODELS:
        model_id   = model_cfg["id"]
        max_tokens = model_cfg["max_tokens"]

        try:
            logger.info(f"[Groq] Trying: {model_id}")

            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user",   "content": user_message},
                ],
                max_tokens=max_tokens,
                temperature=0.72,
                top_p=0.9,
                stream=False,
            )

            if response and response.choices:
                result = response.choices[0].message.content.strip()
                if result:
                    logger.info(f"[Groq] ✅ Success: {model_id} ({len(result)} chars)")
                    return result

        except Exception as exc:
            err = str(exc)[:200]
            logger.warning(f"[Groq] ❌ {model_id} failed: {err}")
            continue

    logger.warning("[Groq] All models failed")
    return None


def test_groq_api():
    """Quick connectivity test for Groq API"""
    print("=" * 60)
    print("TESTING GROQ API")
    print("=" * 60)

    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not api_key:
        print("\n❌ GROQ_API_KEY not set")
        print("   → Get a free key at https://console.groq.com")
        return False

    print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")

    response = call_groq_api("I'm feeling stressed about my work. Any advice?")

    if response:
        print(f"\n✅ SUCCESS!\nResponse: {response}")
        return True
    else:
        print("\n❌ FAILED")
        return False



if __name__ == "__main__":
    test_groq_api()
