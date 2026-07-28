# Changelog

All notable changes to HOMA are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Vision fallback: send a screenshot to `VISION_MODEL` when a page resists text parsing (in progress).

---

## [1.1.0] — 2026-07-28

### Added
- **Live step streaming** — `POST /api/stream` emits Server-Sent Events (`step` … `final`) so the
  dashboard shows each tool call as it happens.
- `POST /api/forget` to clear a session's conversation memory, plus a button in the web UI.
- `python main.py check` — diagnoses the model endpoint, reports proxy interference and lists model ids.
- **Docker support**: `Dockerfile`, `docker-compose.yml` with Chromium and persistent volumes.
- Repository hardening for open source: CI (ruff + pytest + Docker build), issue/PR templates,
  Dependabot, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- Brand assets and documentation set: cover, logo, architecture diagram, screenshots,
  `docs/API.md`, `docs/TOOLS.md`, `docs/TROUBLESHOOTING.md`, and a Persian `README.fa.md`.

### Changed
- Read-only tool calls in a single step now run **concurrently**; dangerous ones stay serialized
  behind the confirmation gate.
- The system prompt pushes the agent to be persistent and to inspect real selectors before acting.
- Telegram polling uses `drop_pending_updates=True`, so a crashed bot no longer replays old commands.

### Security
- Documented the prompt-injection risk surface and the operator hardening checklist.

---

## [1.0.0] — 2026-06-xx

### Added
- Agent core with an OpenAI-compatible tool-calling loop and `MAX_STEPS` ceiling.
- Auto-loading plugin registry (`plugins/` → `ToolRegistry` → JSON schema).
- Tool families: browser, system, web, mail, files, memory, schedule, utility, desktop.
- SQLite memory (per-session history + long-term facts) and an APScheduler job store.
- Telegram bot with inline Allow / Deny confirmation, and a single-file web dashboard.
- `security/guard.py`: shell blocklist, path guard and feature flags.

[Unreleased]: https://github.com/sadult/homa/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/sadult/homa/releases/tag/v1.1.0
[1.0.0]: https://github.com/sadult/homa/releases/tag/v1.0.0
