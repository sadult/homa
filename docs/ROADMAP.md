# Roadmap

HOMA's north star: **a personal agent that never lands** — always available, always allowed to act,
never renting your data to someone else's cloud.

| Version | Milestone | Status |
|---|---|---|
| v1.0 | Agent core, plugin registry, browser/system/web/mail/files/memory/schedule, Telegram + Web | ✅ shipped |
| v1.1 | SSE live step streaming, session memory reset, `main.py check`, Docker, OSS repo hardening | ✅ shipped |
| v1.2 | **Vision fallback** — screenshot → `VISION_MODEL` when text parsing fails | 🚧 in progress |
| v1.3 | **Voice** — Telegram voice notes transcribed (Whisper) straight into the agent | 📋 planned |
| v1.4 | **Profiles & parallel sessions** — keyed browser contexts, per-profile memory | 📋 planned |
| v1.5 | **Approval policies** — per-tool rules ("always allow `files.write` under ~/Downloads") | 📋 planned |
| v2.0 | **Mobile client** over the REST API | 🔭 exploring |
| v2.1 | **Push notifications** for scheduled jobs (FCM/APNs) | 🔭 exploring |
| v2.2 | **Plugin marketplace + hot reload** | 🔭 exploring |

---

## v1.2 — Vision fallback

Some pages are unreadable as text: canvas apps, image-only PDFs, aggressive SPAs. The plan:
`browser.screenshot` → `VISION_MODEL` → element coordinates → click. Text parsing stays the default
because it is cheaper, faster and far more reliable; vision is the escape hatch.

## v1.3 — Voice

Telegram voice note → Whisper (local or API) → the exact same `Agent.run`. Speaking a command while
walking is the most natural interface for a hands-on assistant.

## v1.4 — Profiles & parallel sessions

Today one browser context is shared. Keyed contexts would let HOMA hold *work* and *personal*
sessions at once and run two tasks in parallel without cross-contaminating cookies.

## v1.5 — Approval policies

Confirmation is currently binary. A tiny rules file could express *"auto-allow `files.write` inside
~/Downloads, always ask for `mail.send`, never allow `system.run_command`"* — keeping safety while
removing friction from the boring 90%.

## v2.0 — Mobile client

The REST API is already the product boundary, so the phone stays a thin client:

1. Host HOMA on your laptop or home server.
2. Expose it privately (Tailscale / Cloudflare Tunnel), never a raw open port.
3. A chat screen POSTs to `/api/stream` with the bearer token and renders `step` events live.
4. Reuse the dashboard palette so both clients feel like one product.

See [API.md](API.md).

---

## Non-goals

- **A hosted SaaS.** HOMA is local-first on purpose; a cloud version would defeat the point.
- **CAPTCHA solving or anti-bot evasion.** Log in yourself and hand over the tab.
- **A general chatbot.** If a task needs no tools, HOMA is the wrong tool.
- **Heavyweight orchestration frameworks.** The loop is ~150 readable lines; it stays that way.

## Want to influence this?

Open a [feature request](https://github.com/sadult/homa/issues/new/choose) — plugin ideas that
unlock a whole new category of tasks get prioritized.
