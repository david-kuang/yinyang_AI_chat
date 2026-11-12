"""
Multi-provider FastAPI chat service: Gemini + Groq.

Automatic mode benchmarks configured providers once (using a tiny prompt),
chooses the fastest successful provider, and falls back to the other provider
if the selected provider later fails.

Environment variables:
    GEMINI_API_KEY   Google Gemini API key (optional)
    GROQ_API_KEY     Groq API key (optional)
    AI_PROVIDER      auto (default), gemini, or groq
    GEMINI_MODEL     defaults to gemini-3.8-flash
    GROQ_MODEL       defaults to openai/gpt-oss-120b

Install:
    pip install -r requirements.txt

Run:
    uvicorn multi_api_keys:app --reload
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from google import genai
from google.genai import types
from openai import OpenAI


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").strip().lower()

SYSTEM_INSTRUCTION = "You are a helpful, friendly AI chat assistant."

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

gemini_client = (
    genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
)
groq_client = (
    OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        timeout=45.0,
        max_retries=1,
    )
    if GROQ_API_KEY
    else None
)

app = FastAPI(title="Multi-Provider AI Web Chat", version="2.0.0")

# Cached automatic selection. It is decided on the first chat request.
_selected_provider: Optional[str] = None
_selection_lock = asyncio.Lock()
_provider_stats: Dict[str, Dict[str, Any]] = {
    "gemini": {"configured": bool(gemini_client), "latency_ms": None, "error": None},
    "groq": {"configured": bool(groq_client), "latency_ms": None, "error": None},
}


# ---------------------------------------------------------------------------
# Provider calls
# ---------------------------------------------------------------------------

def _call_gemini(message: str, max_output_tokens: int = 1024) -> str:
    """Send a prompt to Gemini and return its text response."""
    if gemini_client is None:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=max_output_tokens,
        ),
    )
    answer = response.text
    if not answer:
        raise RuntimeError("Gemini returned an empty response.")
    return answer


def _call_groq(message: str, max_output_tokens: int = 1024) -> str:
    """Send a prompt to Groq's OpenAI-compatible chat-completions API."""
    if groq_client is None:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": message},
        ],
        max_tokens=max_output_tokens,
    )
    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError("Groq returned an empty response.")
    return answer


def _provider_call(provider: str, message: str, max_output_tokens: int = 1024) -> str:
    """Dispatch a prompt to the named provider."""
    if provider == "gemini":
        return _call_gemini(message, max_output_tokens)
    if provider == "groq":
        return _call_groq(message, max_output_tokens)
    raise ValueError(f"Unsupported provider: {provider}")


async def _probe_provider(provider: str) -> Tuple[str, Optional[float], Optional[str]]:
    """Measure a provider's response time with a tiny test prompt."""
    started = time.perf_counter()
    try:
        await asyncio.to_thread(
            _provider_call,
            provider,
            "Reply with exactly: OK",
            8,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        _provider_stats[provider]["latency_ms"] = round(elapsed_ms, 1)
        _provider_stats[provider]["error"] = None
        return provider, elapsed_ms, None
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        _provider_stats[provider]["latency_ms"] = None
        _provider_stats[provider]["error"] = error
        return provider, None, error


async def _choose_provider() -> str:
    """
    Choose the provider for this process.

    AI_PROVIDER=gemini/groq forces that provider. In auto mode, both configured
    providers are probed concurrently and the fastest successful one is cached.
    """
    global _selected_provider

    if AI_PROVIDER not in {"auto", "gemini", "groq"}:
        raise HTTPException(
            status_code=500,
            detail="AI_PROVIDER must be 'auto', 'gemini', or 'groq'.",
        )

    if AI_PROVIDER in {"gemini", "groq"}:
        forced_client = gemini_client if AI_PROVIDER == "gemini" else groq_client
        if forced_client is None:
            raise HTTPException(
                status_code=503,
                detail=f"{AI_PROVIDER.upper()} was selected but its API key is not configured.",
            )
        return AI_PROVIDER

    if _selected_provider:
        return _selected_provider

    async with _selection_lock:
        if _selected_provider:
            return _selected_provider

        configured = [
            name
            for name, client in (
                ("gemini", gemini_client),
                ("groq", groq_client),
            )
            if client is not None
        ]

        if not configured:
            raise HTTPException(
                status_code=503,
                detail="No API key configured. Set GEMINI_API_KEY and/or GROQ_API_KEY.",
            )

        if len(configured) == 1:
            _selected_provider = configured[0]
            return _selected_provider

        results = await asyncio.gather(
            *(_probe_provider(name) for name in configured)
        )
        successful = [item for item in results if item[1] is not None]

        if not successful:
            errors = {
                name: _provider_stats[name]["error"]
                for name in configured
            }
            raise HTTPException(
                status_code=503,
                detail={"message": "Both AI providers failed their connection tests.", "errors": errors},
            )

        _selected_provider = min(successful, key=lambda item: item[1])[0]
        return _selected_provider


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Incoming chat request."""
    message: str = Field(..., min_length=1, max_length=50000)


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Answer a chat message using the fastest available configured provider."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    primary = await _choose_provider()
    fallback = "groq" if primary == "gemini" else "gemini"

    try:
        reply = await asyncio.to_thread(_provider_call, primary, message, 2048)
        return {
            "reply": reply,
            "provider": primary,
            "model": GEMINI_MODEL if primary == "gemini" else GROQ_MODEL,
            "fallback_used": False,
        }
    except Exception as primary_error:
        _provider_stats[primary]["error"] = f"{type(primary_error).__name__}: {primary_error}"

        fallback_client = gemini_client if fallback == "gemini" else groq_client
        if fallback_client is None:
            raise HTTPException(
                status_code=502,
                detail=f"{primary} request failed and no fallback API key is configured.",
            )

        try:
            reply = await asyncio.to_thread(_provider_call, fallback, message, 2048)
            # Remember the provider that just succeeded for subsequent requests.
            global _selected_provider
            if AI_PROVIDER == "auto":
                _selected_provider = fallback
            return {
                "reply": reply,
                "provider": fallback,
                "model": GEMINI_MODEL if fallback == "gemini" else GROQ_MODEL,
                "fallback_used": True,
                "primary_error": str(primary_error),
            }
        except Exception as fallback_error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Both providers failed to answer the request.",
                    "primary_error": str(primary_error),
                    "fallback_error": str(fallback_error),
                },
            )


@app.get("/providers")
async def provider_status():
    """Report configured providers and the current automatic selection."""
    return {
        "mode": AI_PROVIDER,
        "selected_provider": _selected_provider,
        "providers": {
            "gemini": {
                **_provider_stats["gemini"],
                "model": GEMINI_MODEL,
            },
            "groq": {
                **_provider_stats["groq"],
                "model": GROQ_MODEL,
            },
        },
        "selection_note": (
            "In auto mode, the first /chat request benchmarks configured providers "
            "with a small test prompt. The fastest successful provider is selected."
        ),
    }


# ---------------------------------------------------------------------------
# Optional static frontend
# ---------------------------------------------------------------------------

current_dir = Path(__file__).resolve().parent
static_dir = current_dir / "static"

if static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def serve_index():
        """Serve static/index.html when the frontend directory exists."""
        index_file = static_dir / "index.html"
        if not index_file.is_file():
            raise HTTPException(status_code=404, detail="static/index.html not found.")
        return FileResponse(str(index_file))
