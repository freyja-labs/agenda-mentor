# Working in this repository

This is a research agenda tracker. `data/*.yaml` is the source of truth; `site/` is generated and ignored by git.

- Run `python scripts/build.py --check` after every data edit and fix any error before committing.
- Prefer `python scripts/agenda.py set|decide|add-action` for routine edits; it keeps comments and order.
- Never delete items. Use `status: dropped` (actions, milestones), `stage: pass` or `declined` (funding), or `status: pass` (external dates you are not pursuing).
- IDs are stable and double as calendar identifiers. New IDs continue the sequence.
- Dates are ISO (`YYYY-MM-DD`). External dates carry a `confidence` level and a `source` URL; do not mark a date `verified` without checking the organizer or funder.
- Ask the owner before naming a sponsor, partner, or collaborator who has not agreed to be named.
- GitHub Pages is public. The pages job publishes only the dashboard encrypted by `scripts/protect.py`; never deploy `site/`, `docs/`, or `data/` to Pages.
