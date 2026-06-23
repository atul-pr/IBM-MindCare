"""
Hugging Face AI Module - Mental Health Support
Uses InferenceClient SDK (routes via router.huggingface.co)

MODEL PRIORITY (based on live testing):
  1. meta-llama/Meta-Llama-3-8B-Instruct  — proven reliable, system-role ✅
  2. meta-llama/Meta-Llama-3.1-8B-Instruct — newer Llama 3.1, system-role ✅
  3. mistralai/Mistral-7B-Instruct-v0.3    — fast, system-role ✅
  4. Qwen/Qwen2.5-7B-Instruct             — high quality, system-role ✅
  5. Qwen/Qwen2.5-72B-Instruct            — last resort, very high quality
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# On Railway, the home dir is read-only — redirect ALL HuggingFace caches to /tmp
# HF_HOME covers: models, datasets, tokenizers (replaces deprecated TRANSFORMERS_CACHE)
os.environ.setdefault('HF_HOME', '/tmp/hf_cache')

load_dotenv()

logger = logging.getLogger(__name__)

# Hugging Face Configuration — key is read dynamically per-request, not at import time
# This ensures Railway env vars are always picked up correctly.
HF_API_KEY = None  # resolved inside call_huggingface_api()

# System prompt — rich but concise to stay under token budget
SYSTEM_PROMPT = (
    "You are HealSpace, a compassionate AI mental health support companion for India. "
    "Your role is to listen with empathy, validate feelings, and offer gentle evidence-based coping strategies. "
    "Tone: warm, non-judgmental, conversational. "
    "Rules: never diagnose, never prescribe medication, always encourage professional help for serious issues. "
    "Keep responses to 2-4 sentences (under 120 words). Use simple, caring language. "
    "If the user mentions crisis or self-harm, gently redirect to the Kiran helpline: 1800-599-0019."
)

# ---------------------------------------------------------------------------
# MODEL REGISTRY
# Each entry: (model_id, supports_system_role, notes)
# Ordered by: reliability → quality → speed
# Models that DON'T support system role get the prompt merged into user turn.
# ---------------------------------------------------------------------------
MODELS = [
    # ── Tier 1: Proven reliable from live logs ─────────────────────────────
    {
        "id": "meta-llama/Meta-Llama-3-8B-Instruct",
        "system_role": True,
        "max_tokens": 200,
        "note": "Primary — proven reliable, fast, good quality"
    },
    # ── Tier 2: Newer / higher quality fallbacks ───────────────────────────
    {
        "id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "system_role": True,
        "max_tokens": 200,
        "note": "Llama 3.1 — improved instruction following"
    },
    {
        "id": "mistralai/Mistral-7B-Instruct-v0.3",
        "system_role": True,
        "max_tokens": 200,
        "note": "Mistral 7B — fast & reliable"
    },
    {
        "id": "Qwen/Qwen2.5-7B-Instruct",
        "system_role": True,
        "max_tokens": 200,
        "note": "Qwen 2.5 7B — high quality, multilingual"
    },
    # ── Tier 3: Large model last resort ───────────────────────────────────
    {
        "id": "Qwen/Qwen2.5-72B-Instruct",
        "system_role": True,
        "max_tokens": 250,
        "note": "72B — best quality, slower"
    },
]

# Per-request timeout in seconds. 25s balances reliability vs user wait.
REQUEST_TIMEOUT = 25


def _build_messages(system_content: str, user_message: str, supports_system: bool, history: list = None) -> list:
    """
    Build the messages list with conversation history.
    For models that don't support a 'system' role, merge the system prompt
    into the first user turn (avoids the 'System role not supported' error).
    """
    if history is None:
        history = []

    if supports_system:
        messages = [{"role": "system", "content": system_content}]
        for msg in history[-8:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})
        return messages
    else:
        # Merge system + history + user into a single user turn
        history_text = ""
        for msg in history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"\n{role}: {msg['content']}"
        merged = f"[Instructions: {system_content}]{history_text}\n\nUser: {user_message}"
        return [{"role": "user", "content": merged}]


def call_huggingface_api(user_message: str, context: str = "", history: list = None) -> Optional[str]:
    """
    Call HuggingFace via InferenceClient.
    Tries models in priority order; skips to next on any failure.
    Returns the first successful response, or None if all fail.
    """
    if history is None:
        history = []

    # Read key dynamically so Railway env vars are always picked up
    hf_key = os.getenv('HF_API_KEY', '').strip()
    if not hf_key or hf_key in ('', 'your-huggingface-api-key-here'):
        logger.warning("[HF] HF_API_KEY not set — skipping HuggingFace")
        return None

    logger.info(f"[HF] API key detected: {hf_key[:8]}... — starting inference")

    # Enrich system prompt with RAG context if available
    system_content = SYSTEM_PROMPT
    if context:
        system_content += f"\n\nRelevant mental health context:\n{context[:400]}"

    for model_cfg in MODELS:
        model_id    = model_cfg["id"]
        max_tokens  = model_cfg["max_tokens"]
        sys_role_ok = model_cfg["system_role"]

        messages = _build_messages(system_content, user_message, sys_role_ok, history)

        try:
            logger.info(f"[HF] Trying model: {model_id}")
            client = InferenceClient(model=model_id, token=hf_key, timeout=REQUEST_TIMEOUT)

            response = client.chat.completions.create(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.72,
                top_p=0.9,
            )

            if response and response.choices:
                result = response.choices[0].message.content.strip()
                if result:
                    logger.info(f"[HF] ✅ Success: {model_id} ({len(result)} chars)")
                    return result

        except Exception as exc:
            logger.warning(f"[HF] ❌ {model_id} failed: {str(exc)[:200]}")
            continue

    logger.error("[HF] All models failed")
    return None


def test_hf_api():
    """Test function to verify HF API connectivity"""
    print("=" * 60)
    print("TESTING HUGGING FACE API")
    print("=" * 60)

    if not HF_API_KEY or HF_API_KEY in ('', 'your-huggingface-api-key-here'):
        print("\n❌ No API key configured")
        return False

    print(f"\nAPI Key: {HF_API_KEY[:10]}...{HF_API_KEY[-4:]}")

    test_message = "I'm feeling very anxious and stressed about my exams."
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
