"""
llm_utils.py

Utility functions for OpenAI GPT chat completions (OpenAI Python SDK v1.x).
"""

import os
from typing import List, Dict, Any, Optional
from config import Config

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

_client = None

def get_openai_client():
    global _client
    if _client is None and OpenAI and Config.OPENAI_API_KEY:
        _client = OpenAI(api_key=Config.OPENAI_API_KEY)
    return _client


def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    stop: Optional[List[str]] = None,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Call OpenAI's chat completion API (v1.x) and return the response text.
    """
    client = get_openai_client()
    if not client:
        print("[llm_utils] OpenAI API not available or API key missing. Falling back to mock response.")
        return "[MOCK LLM RESPONSE]"

    model = model or Config.OPENAI_MODEL

    chat_messages = []
    if system_prompt:
        chat_messages.append({"role": "system", "content": system_prompt})
    chat_messages.extend(messages)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[llm_utils] OpenAI API error: {e}")
        return f"[LLM ERROR: {e}]" 