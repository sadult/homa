# Security Policy

HOMA runs on your personal machine with access to your browser, files, shell and mailbox.
Security issues are therefore taken seriously.

## Supported versions

| Version | Supported |
|---|---|
| 1.1.x | ✅ |
| 1.0.x | ⚠️ critical fixes only |
| < 1.0 | ❌ |

## Reporting a vulnerability

**Please do not open a public issue.**

Use GitHub's [private vulnerability reporting](../../security/advisories/new), or contact the maintainer
directly. Include:

- a description of the issue and its impact,
- reproduction steps or a proof of concept,
- affected version, OS and configuration flags.

You can expect an acknowledgement within **72 hours** and a status update within **7 days**.
Please give a reasonable window for a fix before public disclosure.

## Hardening checklist for operators

- [ ] Keep `ENABLE_SHELL=false` and `ENABLE_FILE_WRITE=false` unless you truly need them.
- [ ] Keep `REQUIRE_CONFIRMATION=true`; never enable web *auto-confirm* on an exposed instance.
- [ ] Use a long random `WEB_AUTH_TOKEN` (e.g. `openssl rand -hex 32`).
- [ ] Keep `WEB_HOST=127.0.0.1`. For remote access use **Tailscale** or a **Cloudflare Tunnel** with access
      control — never port-forward HOMA directly.
- [ ] Restrict `ALLOWED_TELEGRAM_IDS` to your own numeric id.
- [ ] Use app-specific mail passwords, never your primary account password.
- [ ] Run HOMA under a dedicated OS user with limited file permissions.
- [ ] Keep `.env`, `homa.db`, screenshots and downloads out of version control (already git-ignored).

## Known risk surface (by design)

| Surface | Risk | Mitigation |
|---|---|---|
| Browser automation | The agent acts inside your logged-in sessions | Confirmation gate; run with a separate Chrome profile |
| `system.run_command` | Arbitrary command execution | Off by default; blocklist; per-call confirmation |
| `files.write` | Overwriting local files | Off by default; path guard; per-call confirmation |
| `mail.send` | Sending mail as you | Marked dangerous; confirmation required |
| Prompt injection | A malicious web page can try to instruct the agent | Keep confirmations on; avoid auto-confirm on untrusted pages |

Prompt injection through page content is an open research problem. Treat any page HOMA reads as
untrusted input, and keep dangerous tools gated.
