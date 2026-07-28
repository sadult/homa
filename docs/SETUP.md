# Setup guide

## 1. Prerequisites

| | Minimum |
|---|---|
| Python | 3.10+ |
| Disk | ~500 MB (Chromium) |
| Model | Any OpenAI-compatible endpoint **with tool calling** |
| Optional | Telegram bot token from [@BotFather](https://t.me/BotFather) |

## 2. Install

```bash
git clone https://github.com/sadult/homa.git
cd homa

python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

## 3. Configure

```bash
cp .env.example .env
```

Minimum viable `.env`:

```dotenv
NINEROUTER_API_KEY=sk-...
NINEROUTER_BASE_URL=http://localhost:20128/v1
MODEL=gpt-4o-mini
WEB_AUTH_TOKEN=<openssl rand -hex 32>
```

Add Telegram if you want it in your pocket:

```dotenv
TELEGRAM_BOT_TOKEN=123456:ABC-...
ALLOWED_TELEGRAM_IDS=111111111
```

Get your numeric id from [@userinfobot](https://t.me/userinfobot).

## 4. Verify the model endpoint

```bash
python main.py check
```

This prints the endpoint, warns if a proxy is intercepting localhost, and lists every model id the
gateway exposes — copy an exact id into `MODEL`.

## 5. Run

```bash
python main.py both      # Telegram + web dashboard (default)
python main.py web       # dashboard + REST API only
python main.py telegram  # bot only
python main.py cli "open example.com and read the title"
```

Dashboard: <http://127.0.0.1:8000> → ⚙ Settings → paste `WEB_AUTH_TOKEN`.

## 6. Attach to your own Chrome (recommended)

So HOMA can work inside sessions you are already logged into — no passwords stored anywhere:

```bash
# Windows
chrome.exe --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

```dotenv
CHROME_CDP_URL=http://127.0.0.1:9222
```

Then: *"connect to my open browser and answer the questions on this page"*.

> Tip: use a separate Chrome profile for automation (`--user-data-dir=...`) so the agent never touches
> your main session.

## 7. Enable advanced tools (optional)

```dotenv
ENABLE_SHELL=true        # unlocks system.run_command
ENABLE_FILE_WRITE=true   # unlocks files.write
```

Both still require per-action confirmation while `REQUIRE_CONFIRMATION=true`. Keep it that way.

## 8. Run it as a service

<details>
<summary><b>systemd (Linux)</b></summary>

```ini
# /etc/systemd/system/homa.service
[Unit]
Description=HOMA — Hands-On Machine Assistant
After=network-online.target

[Service]
Type=simple
User=homa
WorkingDirectory=/opt/homa
EnvironmentFile=/opt/homa/.env
ExecStart=/opt/homa/.venv/bin/python main.py both
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now homa
journalctl -u homa -f
```
</details>

<details>
<summary><b>Docker</b></summary>

```bash
cp .env.example .env
docker compose up -d --build
docker compose logs -f
```

`homa.db` and `downloads/` are bind-mounted, so memory and schedules survive rebuilds.
</details>

<details>
<summary><b>Windows Task Scheduler</b></summary>

Create a task that runs at logon:
`C:\path\to\homa\.venv\Scripts\python.exe C:\path\to\homa\main.py both`
with "Start in" set to the project folder.
</details>

## 9. Reach it from outside your LAN

Do **not** port-forward. Use one of:

- **Tailscale** — `tailscale up`, then browse to `http://<machine>:8000` from any of your devices.
- **Cloudflare Tunnel** — `cloudflared tunnel --url http://127.0.0.1:8000`, protected with Access.

And keep `WEB_AUTH_TOKEN` long and random either way.

Stuck? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
