# Tool catalog

Every capability HOMA has is a **tool** registered by a plugin. This is the shipped catalog;
`GET /api/tools` (or `/tools` on Telegram) always shows the live list.

⚠ = `dangerous=True` — requires explicit confirmation, and often a feature flag.

---

## 🌐 browser — `plugins/browser.py`

Playwright Chromium, headless or attached to your own Chrome over CDP.

| Tool | Arguments | Does |
|---|---|---|
| `browser.goto` | `url` | Navigate and wait for the page to settle |
| `browser.read` | `selector?` | Extract readable text (truncated to fit context) |
| `browser.inspect` | `selector?` | List real, clickable elements with their selectors |
| `browser.extract_form` | — | Every question/field with its options **and selectors** |
| `browser.click` | `selector` | Click an element |
| `browser.type` | `selector`, `text` | Type into a field |
| `browser.fill_form` | `answers[]` | Fill many fields in one call |
| `browser.scroll` | `direction`, `amount?` | Scroll the page |
| `browser.back` | — | History back |
| `browser.screenshot` | `path?` | Capture the viewport (feeds `VISION_MODEL`) |
| `browser.connect_existing` | — | Attach to your open Chrome via `CHROME_CDP_URL` |

**Golden rule:** the agent must call `inspect` or `extract_form` before it clicks or types. Selectors
are read from the page, never invented.

---

## 🖥 system — `plugins/system.py`

| Tool | Arguments | Does |
|---|---|---|
| `system.disk_usage` | `path?` | Free/total space per drive |
| `system.list_dir` | `path` | Directory listing with sizes and mtimes |
| `system.info` | — | OS, CPU, RAM, uptime |
| `system.processes` | `filter?` | Running processes |
| `system.open` | `path` | Open a file/folder/app with the OS handler |
| `system.run_command` ⚠ | `command` | Shell execution — needs `ENABLE_SHELL=true` + confirmation |

---

## 🔎 web — `plugins/web.py`

| Tool | Arguments | Does |
|---|---|---|
| `web.fetch` | `url` | HTTP GET, HTML → clean text |
| `web.search` | `query` | Web search results |
| `web.download` | `url`, `path?` | Download a file to `downloads/` |

---

## 📬 mail — `plugins/mail.py`

| Tool | Arguments | Does |
|---|---|---|
| `mail.check` | `folder?`, `unread_only?`, `limit?` | Read recent messages over IMAP |
| `mail.send` ⚠ | `to`, `subject`, `body` | Send over SMTP |

Use app-specific passwords, never your primary account password.

---

## 📁 files — `plugins/files.py`

| Tool | Arguments | Does |
|---|---|---|
| `files.search` | `pattern`, `root?` | Glob/recursive search |
| `files.read` | `path` | Read a text file (truncated) |
| `files.write` ⚠ | `path`, `content` | Write a file — needs `ENABLE_FILE_WRITE=true` + confirmation |

---

## 🧠 memory — `plugins/memory_tools.py`

| Tool | Arguments | Does |
|---|---|---|
| `memory.remember` | `key`, `value` | Store a durable fact |
| `memory.recall` | `key` | Fetch one fact |
| `memory.search` | `query` | Search stored facts |
| `memory.list` | — | List everything remembered |
| `memory.forget` | `key` | Delete a fact |

Conversation history is separate and per-session; clear it with `/api/forget` or the UI button.

---

## ⏰ schedule — `plugins/schedule_tools.py`

| Tool | Arguments | Does |
|---|---|---|
| `schedule.add` | `name`, `when`, `command` | Create a recurring or one-off job |
| `schedule.list` | — | Show jobs and next run times |
| `schedule.remove` | `name` | Delete a job |

Jobs live in a SQLite APScheduler store, so they survive restarts. A job simply re-runs `Agent.run`
with its stored command and delivers the answer to the interface that created it.

---

## 🧰 utility — `plugins/utilities.py`

| Tool | Arguments | Does |
|---|---|---|
| `clipboard.get` | — | Read the clipboard |
| `clipboard.set` | `text` | Write to the clipboard |
| `notify.desktop` | `title`, `message` | Native desktop notification |
| `time.now` | `tz?` | Current date/time (defaults to system tz) |

---

## 🖱 desktop — `plugins/desktop.py`

Window and application helpers (focus, list, launch). Availability depends on your OS.

---

## Adding your own

One file in `plugins/`, one `register(registry)` function — see [PLUGINS.md](PLUGINS.md).
Document new tools here and in the README table when you open a PR.
