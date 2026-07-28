# REST API

Base URL: `http://WEB_HOST:WEB_PORT` (default `http://127.0.0.1:8000`).

Every `/api/*` endpoint requires the token from `.env`:

```http
Authorization: <WEB_AUTH_TOKEN>
# or
Authorization: Bearer <WEB_AUTH_TOKEN>
```

A wrong or missing token returns `401 {"detail":"Invalid token"}`.

---

## `POST /api/command`

Run a command and wait for the final answer.

**Request**

```json
{
  "command": "how much free space is on drive C?",
  "session": "web",
  "auto_confirm": false
}
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `command` | string | — | Natural language, Persian or English |
| `session` | string | `"web"` | Conversation bucket; separate sessions have separate memory |
| `auto_confirm` | bool | `false` | Approve dangerous tools without asking. Use with care |

**Response**

```json
{
  "result": "Drive C: 118.4 GB free of 476.9 GB (75% used).",
  "steps": [
    {"t": "0.2", "msg": "command: how much free space…", "level": "info"},
    {"t": "1.1", "msg": "system.disk_usage(path=C:\\)", "level": "info"},
    {"t": "1.3", "msg": "✓ system.disk_usage", "level": "ok"}
  ]
}
```

---

## `POST /api/stream`

Same body as `/api/command`, but responds with **Server-Sent Events** so you can render progress live.

```text
data: {"type":"step","t":"1.1","msg":"browser.goto(url=…)","level":"info"}
data: {"type":"step","t":"3.4","msg":"✓ browser.goto","level":"ok"}
data: {"type":"final","result":"Here are today's headlines…"}
```

```bash
curl -N http://127.0.0.1:8000/api/stream \
  -H "Authorization: $WEB_AUTH_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"command":"open example.com and read the title","session":"cli"}'
```

Errors inside the run arrive as a `final` event whose `result` starts with `⚠️ Error:` — the stream
itself stays `200`.

---

## `POST /api/forget`

Clear the stored conversation history for one session.

```json
{ "session": "web" }
```

```json
{ "cleared": 24 }
```

---

## `GET /api/tools`

```json
{
  "categories": {
    "browser": ["browser.goto", "browser.read", "..."],
    "system": ["system.disk_usage", "..."]
  },
  "count": 42
}
```

---

## `GET /`

Serves the dashboard (`interfaces/web/static/index.html`). No token needed to load the page — the
token is entered in the UI and used for the API calls it makes.

---

## Client examples

<details><summary><b>Python</b></summary>

```python
import httpx

r = httpx.post(
    "http://127.0.0.1:8000/api/command",
    headers={"Authorization": TOKEN},
    json={"command": "summarize my unread mail", "session": "scripts"},
    timeout=300,
)
print(r.json()["result"])
```
</details>

<details><summary><b>JavaScript (SSE)</b></summary>

```js
const res = await fetch("/api/stream", {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: token },
  body: JSON.stringify({ command, session: "web", auto_confirm: false }),
});
const reader = res.body.getReader();
const dec = new TextDecoder();
for (;;) {
  const { value, done } = await reader.read();
  if (done) break;
  for (const line of dec.decode(value).split("\n")) {
    if (line.startsWith("data: ")) handle(JSON.parse(line.slice(6)));
  }
}
```
</details>

---

## Building a mobile client

The phone stays a thin remote control; the brain never leaves your machine.

1. Host HOMA on your laptop or home server.
2. Expose it privately over **Tailscale** or a **Cloudflare Tunnel** — never a raw open port.
3. Build a chat screen that POSTs to `/api/stream` with the bearer token and renders `step` events
   as they arrive.
4. Reuse the dashboard's palette (`interfaces/web/static/index.html`) for a consistent look.
5. For push notifications, have scheduled jobs hit a device token in addition to Telegram.

## Notes and limits

- There is no rate limiting — HOMA assumes a single trusted operator.
- Long tasks can run for minutes; set generous client timeouts, or prefer `/api/stream`.
- `MAX_STEPS` bounds every run; the final message says so explicitly when the ceiling is hit.
- Sessions are logical, not authenticated: anyone with the token can read any session's memory.
