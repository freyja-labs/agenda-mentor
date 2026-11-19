# Working in this repository

This is the Agenda Mentor portal: a public site built from `content/`, `data/`, `prompts/`, `templates/`, and `assets/` by `scripts/build.py`. `_site/` is generated and ignored by git.

- Run `python scripts/build.py --check` after every edit and fix any error before committing.
- Everything the build publishes is public. Never add a real agenda, intake, CV, whiteboard photo, review, or tracker data; the tracker template ships fictional sample data only.
- Keep `schema/agenda.schema.json` section keys and `data/anatomy.yaml` keys identical; the build enforces it, and Facultory's Research Agenda tool uses the same keys.
- Prompt placeholders must be in `KNOWN_FIELDS` (`scripts/build.py`) and have a form field in `templates/prompts.html`.
- The schema's `intake` keys match `INTAKE_FIELDS` in `scripts/build.py` and Facultory's `INTAKE_KEYS`; the builder's **Download your answers** file must keep importing into Facultory's Research Agenda tool.
- Every statement about Facultory (`templates/partials/facultory.html`, the prompts handoff, the track, mentors, and about pages) must be true of the Research Agenda tool as shipped. Name no prices or offers; the signup page shows those. Keep the line saying this site and Facultory have the same author.
- Discipline profiles name funder types with examples and keep `verify_note`; do not state a program's current status as fact.
- Writing follows Mike's voice: direct and declarative, American English, Oxford commas, acronyms spelled out at first use, no "not X, but Y" constructions, sentence case.
- Design rules: no card grids; red (`--redpen`) is reserved for things that need verification; the Kalam hand face appears only inside the board drawing.
