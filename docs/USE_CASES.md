# Use cases — things people actually ask HOMA

Every example below is a single natural-language message. Persian works equally well.

---

## 🌐 Browser work

| Command | What HOMA does |
|---|---|
| *"Open this survey and answer the questions."* | `extract_form` → decides answers → `fill_form` → submit |
| *"Log in to my billing dashboard and download this month's invoice."* | Attaches to your Chrome, navigates, downloads (asks first) |
| *"Check these 5 product pages and tell me which is cheapest."* | Parallel reads, one comparison table back |
| *"Book the earliest available slot on this page and confirm."* | Inspect → click → verify → report |
| *"Copy every job title and salary from this listing page into a list."* | Reads, extracts, returns structured text |

## 🖥 Your computer

| Command | What HOMA does |
|---|---|
| *"How much free space is left on drive C?"* | `system.disk_usage` |
| *"Find every PDF in Documents from the last 3 months."* | `files.search` + filtering |
| *"What's eating my RAM right now?"* | `system.processes` sorted by memory |
| *"Open my Downloads folder."* | `system.open` |
| *"Copy this text to my clipboard and pop a reminder on screen."* | `clipboard.set` + `notify.desktop` |

## 📬 Mail

| Command | What HOMA does |
|---|---|
| *"Did Ali email me today?"* | IMAP search, summarised |
| *"Summarise my unread mail in 5 bullets."* | Reads and condenses |
| *"Reply to that message saying I'll send the file tomorrow."* | Drafts, then asks before sending |

## ⏰ On a schedule

| Command | What HOMA does |
|---|---|
| *"Every day at 9am, send me the USD rate."* | Persistent job → Telegram each morning |
| *"Every Monday, check my invoices page and tell me what's due."* | Weekly browser run |
| *"Remind me every 2 hours to stretch."* | Desktop notification loop |
| *"What jobs do I have scheduled?"* | `schedule.list` with next run times |

## 🧠 Memory

| Command | What HOMA does |
|---|---|
| *"Remember my shipping address is …"* | Stores a durable fact |
| *"Use that address to fill this checkout form."* | `memory.recall` → `fill_form` |
| *"Forget my old phone number."* | `memory.forget` |

---

## Composite workflows worth stealing

**Morning briefing**
> *"Every weekday at 8:30: check my unread mail, read the top 3 headlines, tell me today's USD rate,
> and send it all as one message."*

**Expense collector**
> *"On the 1st of each month, log in to my three service dashboards, download the latest invoices to
> ~/Invoices, and tell me the total."*

**Research assistant**
> *"Search for the 5 most recent articles about X, read each one, and give me a comparison table with
> the key claim from each."*

**Form marathon**
> *"I've opened a 40-question form in my Chrome. Connect to it, answer everything consistent with what
> you remember about me, and stop before the final submit."*

---

## Where HOMA is deliberately unhelpful

- Solving CAPTCHAs or evading bot protection
- Acting on accounts that are not yours
- Taking exams or completing assessments on someone's behalf
- Anything that violates a site's terms of service

It is a personal automation tool. Keep it personal.
