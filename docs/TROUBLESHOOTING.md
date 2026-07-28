# Troubleshooting

Start here — it fixes 90% of problems:

```bash
python main.py check
```

---

## Model / endpoint

| Symptom | Cause | Fix |
|---|---|---|
| `FAILED — cannot connect` | Gateway not running, or wrong `NINEROUTER_BASE_URL` | Open the 9Router/Ollama dashboard and copy the exact local endpoint, e.g. `http://localhost:20128/v1` |
| Connects from the browser but not from HOMA | A VPN/proxy captures all traffic | Exclude `localhost` and `127.0.0.1` in the VPN's split-tunnel settings |
| `HTTP 401` | Bad API key | Re-copy `NINEROUTER_API_KEY` |
| `MODEL is not in the list` | Model id typo | Use an exact id printed by `main.py check` |
| Answers arrive very slowly | Large model + long tool loops | Switch to a smaller fast model (`gpt-4o-mini`, `qwen2.5:14b`) |
| `400 tools not supported` | Model has no tool calling | Choose a tool-calling capable model — HOMA cannot work without it |

---

## Browser

| Symptom | Fix |
|---|---|
| `Executable doesn't exist` / Playwright errors | `playwright install chromium` (re-run inside the venv) |
| Linux: missing shared libraries | `playwright install-deps chromium` or use the Docker image |
| `connect_existing` fails | Chrome must be launched with `--remote-debugging-port=9222`, and `CHROME_CDP_URL` must match |
| Agent clicks the wrong thing | It skipped inspection — tell it *"inspect the page first"*, or use a stronger model |
| Page loads blank | Site blocks headless — set `HEADLESS=false` or attach to your real Chrome |
| Login walls / CAPTCHA | By design, HOMA does not solve CAPTCHAs. Log in yourself, then hand the tab over |

---

## Telegram

| Symptom | Fix |
|---|---|
| *Not authorized* | Add your numeric id to `ALLOWED_TELEGRAM_IDS` (get it from [@userinfobot](https://t.me/userinfobot)) |
| Bot silent | Only one process may poll a token — stop other instances |
| Old commands replay after a crash | Already handled via `drop_pending_updates=True`; make sure you are on ≥ v1.1 |
| Confirmation buttons do nothing | The bot restarted mid-task; send the command again |

---

## Web dashboard / API

| Symptom | Fix |
|---|---|
| `401 Invalid token` | The `Authorization` header must equal `WEB_AUTH_TOKEN` exactly (bare or `Bearer <token>`) |
| Steps never stream | A reverse proxy is buffering SSE — disable buffering (`X-Accel-Buffering: no` is already sent) |
| Port already in use | Change `WEB_PORT`, or stop the other process |
| Dashboard reachable from the LAN unintentionally | Keep `WEB_HOST=127.0.0.1` and use Tailscale for remote access |

---

## Agent behaviour

| Symptom | Fix |
|---|---|
| "Reached the step limit" | Raise `MAX_STEPS`, or split the task into smaller commands |
| Stops halfway and asks what to do | Weak model. Prefer GPT-4o-class, Claude 3.5+, Qwen 2.5 32B+ |
| Ignores a dangerous action | That is the guard working — confirm it, or enable the matching flag in `.env` |
| Forgets context between messages | Different `session` values have separate memory — keep it consistent |
| Remembers something wrong | `memory.forget <key>`, or use 🧹 *Clear conversation memory* in the UI |

---

## Data & recovery

- Everything lives in `homa.db` (history, facts, jobs). Delete it for a clean slate — you lose
  memory and schedules, nothing else.
- Back it up with `cp homa.db homa.db.bak` while HOMA is stopped.
- Screenshots and downloads land in the project folder and are git-ignored.

## Still stuck?

Open an issue with your OS, Python version, model id, the command you gave, and the step log.
Never paste API keys, tokens, or mail passwords.
