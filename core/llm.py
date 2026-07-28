from urllib.parse import urlparse

import httpx
from openai import APIConnectionError, OpenAI, RateLimitError

from config import settings

# 9Router exposes an OpenAI-compatible endpoint, so we point the official
# OpenAI SDK at its base_url. Swapping providers is just an .env change.
#
# When the endpoint is on localhost (the normal 9Router setup) we disable
# proxy environment variables (trust_env=False): otherwise a system-wide
# HTTP(S)_PROXY would try to route localhost traffic through the proxy and
# every request would fail with a connection error.
_host = (urlparse(settings.NINEROUTER_BASE_URL).hostname or "").lower()
_is_local = _host in ("localhost", "127.0.0.1", "0.0.0.0", "::1")

_client = OpenAI(
    api_key=settings.NINEROUTER_API_KEY,
    base_url=settings.NINEROUTER_BASE_URL,
    timeout=settings.LLM_TIMEOUT,
    max_retries=1,
    http_client=(
        httpx.Client(trust_env=False, timeout=settings.LLM_TIMEOUT)
        if _is_local
        else None
    ),
)


def chat(messages, tools=None, tool_choice="auto", model=None, temperature=0.2):
    """One round-trip with the model; returns the assistant message object
    (which may contain tool_calls)."""
    kwargs = {
        "model": model or settings.MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice
    try:
        resp = _client.chat.completions.create(**kwargs)
    except RateLimitError as exc:
        raise RuntimeError(
            "The model provider hit its rate limit / quota (HTTP 429). "
            "Free Gemini tiers allow very few requests per day, and one agent "
            "task uses several. Fixes: switch MODEL in .env to another model in "
            "your 9Router dashboard (it has free-tier fallbacks), wait for the "
            "quota to reset, or connect a paid provider. Run `python main.py check` "
            "to see which models you can use."
        ) from exc
    except APIConnectionError as exc:
        raise RuntimeError(
            f"Cannot reach the model endpoint at {settings.NINEROUTER_BASE_URL} "
            "— is 9Router running, and is NINEROUTER_BASE_URL in .env set to the "
            "local endpoint shown in the 9Router dashboard? "
            "Run `python main.py check` to diagnose."
        ) from exc
    return resp.choices[0].message
