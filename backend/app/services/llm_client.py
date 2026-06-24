"""
LLM and embedding client — Ollama (free/local) default, optional OpenAI/Gemini.
"""

import json
import re
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import logger


class LLMConfigurationError(Exception):
    """Raised when AI provider is unavailable or misconfigured."""


def is_ai_configured() -> bool:
    """Return True if the selected provider is ready."""
    if settings.AI_PROVIDER == "ollama":
        return _ollama_server_reachable()
    if settings.AI_PROVIDER == "gemini":
        return bool(settings.GEMINI_API_KEY)
    if settings.AI_PROVIDER == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


def get_ai_setup_hint() -> str:
    """Human-readable setup instructions for the active provider."""
    if settings.AI_PROVIDER == "ollama":
        return (
            "Install Ollama (https://ollama.com), then run:\n"
            f"  ollama pull {settings.OLLAMA_MODEL}\n"
            f"  ollama pull {settings.OLLAMA_EMBEDDING_MODEL}"
        )
    if settings.AI_PROVIDER == "gemini":
        return "Set GEMINI_API_KEY in backend/.env"
    return "Set OPENAI_API_KEY in backend/.env"


def active_chat_model() -> str:
    """Return the chat model name for the active provider."""
    if settings.AI_PROVIDER == "gemini":
        return settings.GEMINI_MODEL
    if settings.AI_PROVIDER == "openai":
        return settings.OPENAI_MODEL
    return settings.OLLAMA_MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    if not texts:
        return []

    if settings.AI_PROVIDER == "gemini":
        return _embed_gemini(texts)
    if settings.AI_PROVIDER == "openai":
        return _embed_openai(texts)
    return _embed_ollama(texts)


def complete_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """Request a JSON object from the configured LLM."""
    if settings.AI_PROVIDER == "gemini":
        raw = _complete_gemini(system_prompt, user_prompt)
    elif settings.AI_PROVIDER == "openai":
        raw = _complete_openai(system_prompt, user_prompt)
    else:
        raw = _complete_ollama(system_prompt, user_prompt)

    return _parse_json_response(raw)


def _ollama_base() -> str:
    return settings.OLLAMA_BASE_URL.rstrip("/")


def _ollama_server_reachable() -> bool:
    try:
        response = httpx.get(f"{_ollama_base()}/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def _embed_ollama(texts: list[str]) -> list[list[float]]:
    if not _ollama_server_reachable():
        raise LLMConfigurationError(
            "Ollama is not running. Start the Ollama app or run `ollama serve`.\n"
            + get_ai_setup_hint()
        )

    try:
        response = httpx.post(
            f"{_ollama_base()}/api/embed",
            json={"model": settings.OLLAMA_EMBEDDING_MODEL, "input": texts},
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings")
        if not embeddings or len(embeddings) != len(texts):
            raise LLMConfigurationError(
                f"Ollama embedding model '{settings.OLLAMA_EMBEDDING_MODEL}' failed. "
                f"Run: ollama pull {settings.OLLAMA_EMBEDDING_MODEL}"
            )
        return embeddings
    except httpx.HTTPError as exc:
        raise LLMConfigurationError(
            f"Ollama embedding error: {exc}. "
            f"Ensure model is pulled: ollama pull {settings.OLLAMA_EMBEDDING_MODEL}"
        ) from exc


def _complete_ollama(system_prompt: str, user_prompt: str) -> str:
    if not _ollama_server_reachable():
        raise LLMConfigurationError(
            "Ollama is not running. Start the Ollama app or run `ollama serve`.\n"
            + get_ai_setup_hint()
        )

    try:
        response = httpx.post(
            f"{_ollama_base()}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
            timeout=settings.OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        content = response.json().get("message", {}).get("content", "{}")
        return content or "{}"
    except httpx.HTTPError as exc:
        raise LLMConfigurationError(
            f"Ollama chat error: {exc}. "
            f"Ensure model is pulled: ollama pull {settings.OLLAMA_MODEL}"
        ) from exc


def _embed_openai(texts: list[str]) -> list[list[float]]:
    if not settings.OPENAI_API_KEY:
        raise LLMConfigurationError("OPENAI_API_KEY is not set")

    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.embeddings.create(
        model=settings.OPENAI_EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    if not settings.GEMINI_API_KEY:
        raise LLMConfigurationError("GEMINI_API_KEY is not set")

    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    vectors: list[list[float]] = []
    for text in texts:
        result = genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document",
        )
        vectors.append(result["embedding"])
    return vectors


def _complete_openai(system_prompt: str, user_prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise LLMConfigurationError("OPENAI_API_KEY is not set")

    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "{}"


def _complete_gemini(system_prompt: str, user_prompt: str) -> str:
    if not settings.GEMINI_API_KEY:
        raise LLMConfigurationError("GEMINI_API_KEY is not set")

    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system_prompt,
        generation_config={
            "temperature": 0.1,
            "response_mime_type": "application/json",
        },
    )
    response = model.generate_content(user_prompt)
    return response.text or "{}"


def _parse_json_response(raw: str) -> dict[str, Any]:
    text = raw.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        logger.error(f"Failed to parse LLM JSON: {text[:500]}")
        raise LLMConfigurationError("LLM returned invalid JSON")
