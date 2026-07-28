## What does this PR do?

<!-- One or two sentences. Link the issue it closes: Closes #123 -->

## Type of change

- [ ] 🔌 New plugin / tool
- [ ] ✨ Feature
- [ ] 🐛 Bug fix
- [ ] 📚 Docs
- [ ] 🧹 Refactor / chore

## How was it tested?

<!-- Commands you gave HOMA, model used, and what it did. Paste the step log if useful. -->

## Safety review

- [ ] No new tool writes, sends, deletes, pays or executes **without** `dangerous=True`
- [ ] Free-form paths / commands go through `security/guard.py`
- [ ] Tool output is truncated so it fits the model context
- [ ] No secrets, tokens, or personal paths in the diff

## Checklist

- [ ] `make lint` passes
- [ ] `make test` passes
- [ ] README / `docs/TOOLS.md` updated if capabilities changed
- [ ] Screenshots attached for UI changes
