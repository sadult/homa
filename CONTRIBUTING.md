# Contributing to HOMA

Thanks for wanting to make the bird fly higher 🕊

HOMA is a personal-scale project, so contributions are reviewed with two questions in mind:
**does it stay simple?** and **does it stay safe?**

---

## Ways to contribute

| | |
|---|---|
| 🐛 **Bug reports** | Use the issue template. Include your OS, Python version, model id, and the step log. |
| 🔌 **New plugins** | The best kind of PR. One plugin per file, one file per PR. |
| 📚 **Docs** | Typos, clearer wording, Persian translations — all welcome. |
| 🎨 **UI polish** | The dashboard is a single self-contained HTML file; keep it dependency-free. |
| 🔒 **Security** | Please read [SECURITY.md](SECURITY.md) first — don't open a public issue. |

---

## Development setup

```bash
git clone https://github.com/sadult/homa.git
cd homa
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
playwright install chromium
cp .env.example .env
```

Useful commands:

```bash
make lint       # ruff check .
make format     # ruff format .
make test       # pytest -q
make run        # python main.py both
make check      # verify the model endpoint
```

---

## Writing a plugin (the golden path)

1. Create `plugins/<area>.py` with a `register(registry: ToolRegistry) -> None` function.
2. Tool names are dotted and lowercase: `area.verb` (e.g. `calendar.add_event`).
3. Handlers are **async** and return JSON-serialisable dicts.
4. Write descriptions **for the model, not for humans** — say exactly when the tool should be used.
5. Anything that writes, deletes, sends, pays, or executes must set `dangerous=True`.
6. Truncate long output; the model pays for every token you return.
7. Never trust free-form paths or commands — route them through `security/guard.py`.

Full guide: [`docs/PLUGINS.md`](docs/PLUGINS.md).

---

## Code style

- Python 3.10+, type hints on public functions.
- [Ruff](https://docs.astral.sh/ruff/) for linting and formatting (config in `pyproject.toml`).
- Keep the core (`core/`, `tools/`) small; capability belongs in `plugins/`.
- No new runtime dependency unless it earns its place — explain why in the PR.

---

## Commit & PR conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat(plugins): add calendar tools
fix(browser): wait for network idle before extract_form
docs(readme): clarify Ollama setup
chore(ci): bump actions/setup-python
```

Before opening a PR:

- [ ] `make lint` and `make test` pass
- [ ] New tools are documented in `docs/TOOLS.md` and the README table
- [ ] Dangerous tools are flagged and gated
- [ ] No secrets, tokens, or personal paths in the diff
- [ ] Screenshots included for UI changes

---

## License of contributions

By contributing you agree that your contribution is licensed under the project's
[PolyForm Noncommercial License 1.0.0](LICENSE).
