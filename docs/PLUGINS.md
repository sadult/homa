# Writing plugins

HOMA's power comes from its plugin system. You never edit the core to add a capability — you drop a
file in `plugins/` that defines `register(registry)`. On startup, `core/plugin_loader.py` imports
every module in that folder and calls it.

---

## Minimal example

`plugins/weather.py`:

```python
import httpx

from tools.registry import Tool, ToolRegistry


async def weather(city: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get("https://wttr.in/" + city, params={"format": "3"})
    return {"report": r.text.strip()}


def register(registry: ToolRegistry) -> None:
    registry.register(Tool(
        name="weather.now",
        description="Get the current weather for a city. Use when the user asks about weather.",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name in English"}},
            "required": ["city"],
        },
        handler=weather,
        category="weather",
    ))
```

Restart HOMA and ask *"what's the weather in Tehran?"*. Done.

---

## The `Tool` contract

| Field | Type | Meaning |
|---|---|---|
| `name` | `str` | Unique dotted id, `area.verb` — e.g. `calendar.add_event` |
| `description` | `str` | **Written for the model.** Say when to use it and when not to |
| `parameters` | `dict` | JSON Schema for the arguments |
| `handler` | `async fn` | Kwargs match the schema; returns JSON-serialisable data |
| `dangerous` | `bool` | `True` ⇒ requires user confirmation before running |
| `category` | `str` | Grouping shown in `/tools` and the API |

---

## Rules that keep the agent reliable

1. **Async everywhere.** Blocking I/O stalls the whole loop — use `httpx.AsyncClient`,
   `asyncio.to_thread` for unavoidable sync libraries.
2. **Return dicts, not prose.** The model reasons better over `{"free_gb": 118.4}` than a sentence.
3. **Budget your tokens.** Truncate long text (`text[:4000]`), paginate lists, and return counts
   instead of dumps. A single greedy tool can eat an entire context window.
4. **Fail loudly but structurally**: `return {"error": "...", "hint": "..."}`. The agent can recover
   from a described failure; it cannot recover from an exception it never sees.
5. **Mark side effects.** Writes, sends, payments, deletions and shell calls → `dangerous=True`.
6. **Never trust free-form input.** Route paths and commands through `security/guard.py`.
7. **Describe enums explicitly** in the schema — models follow `"enum": [...]` far better than prose.
8. **One area per file.** `plugins/calendar.py` may register five `calendar.*` tools; it should not
   register `mail.*`.

---

## Dangerous tool template

```python
from config import settings
from security import guard
from tools.registry import Tool, ToolRegistry


async def delete_file(path: str) -> dict:
    if not settings.ENABLE_FILE_WRITE:
        return {"error": "file writes are disabled", "hint": "set ENABLE_FILE_WRITE=true in .env"}
    safe_path = guard.check_path(path)          # raises / normalises
    safe_path.unlink()
    return {"deleted": str(safe_path)}


def register(registry: ToolRegistry) -> None:
    registry.register(Tool(
        name="files.delete",
        description="Permanently delete a single file. Ask the user before using this.",
        parameters={
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
        handler=delete_file,
        dangerous=True,
        category="files",
    ))
```

---

## Testing a plugin

```bash
python main.py cli "what's the weather in Tehran?"
```

Or call the handler directly:

```python
import asyncio

from plugins.weather import weather

print(asyncio.run(weather("Tehran")))
```

And confirm registration:

```bash
curl -H "Authorization: $WEB_AUTH_TOKEN" http://127.0.0.1:8000/api/tools
```

---

## Plugin ideas worth building

| Plugin | Tools | Why it's fun |
|---|---|---|
| `calendar.py` | `add_event` `agenda` | "Put a meeting at 4pm tomorrow" |
| `notion.py` | `search` `append` | Daily journal written by the agent |
| `spotify.py` | `play` `pause` `search` | Voice-ish control of your music |
| `finance.py` | `rate` `portfolio` | Scheduled market digests |
| `torrent.py` | `add` `status` | Fully hands-off downloads |
| `ssh.py` ⚠ | `run` | Remote box administration |
| `vision.py` | `describe_screenshot` | Handle pages that resist text parsing |

Built something good? Open a PR — see [CONTRIBUTING.md](../CONTRIBUTING.md).
