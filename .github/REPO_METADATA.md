# GitHub repository metadata

Copy-paste this when you create the repo (Settings → General, and the ⚙ next to **About**).

---

## Repository name

```text
homa
```

## Description (the "About" field — 350 char max)

**Short (recommended):**

```text
🕊 HOMA — Hands-On Machine Assistant: a self-hosted, local-first AI agent that drives a real browser, controls your computer, reads mail, remembers, and runs scheduled tasks — from Telegram, a web dashboard, or your terminal. Plugin-native, bilingual (FA/EN), works with any OpenAI-compatible model.
```

**Ultra-short (for social previews and package listings):**

```text
Self-hosted AI agent that actually uses your machine — browser, files, mail and schedules, from Telegram or the web.
```

## Website

```text
https://github.com/sadult/homa#readme
```

## Topics (GitHub limits you to 20)

```text
ai-agent, autonomous-agent, llm, tool-calling, function-calling, browser-automation,
playwright, telegram-bot, fastapi, python, self-hosted, local-first, personal-assistant,
automation, openai-compatible, ollama, web-scraping, rpa, persian, plugin-architecture
```

## Recommended repo settings

- [ ] **Social preview image:** upload `assets/cover.png` (Settings → General → Social preview, 1280×640)
- [ ] Enable **Discussions** (the issue template links to it)
- [ ] Enable **Private vulnerability reporting** (Settings → Security)
- [ ] Enable **Dependabot alerts + security updates**
- [ ] Branch protection on `main`: require the `CI` check to pass
- [ ] Disable **Wiki** and **Projects** unless you plan to use them
- [ ] Add `assets/logo.png` as the organization/profile avatar if you make an org

## Release checklist

1. Update `CHANGELOG.md`.
2. Tag: `git tag -a v1.1.0 -m "HOMA v1.1.0" && git push --tags`.
3. Create the GitHub Release, paste the changelog section, attach `assets/cover.png`.
4. Post the release with a 20-second screen recording of a real task — that is what makes people star it.

## Suggested pinned comment / launch blurb

> **HOMA — Hands-On Machine Assistant.** Most AI assistants can only talk; HOMA acts. It runs on your
> own laptop, drives a real Chrome session, inspects your system, reads your mail, remembers your
> preferences and works on a schedule — and every capability is a drop-in Python plugin.
> Local-first, no agent cloud, works with any OpenAI-compatible model.
