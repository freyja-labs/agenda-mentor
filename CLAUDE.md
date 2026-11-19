# Working in this repository

This is the Agenda Mentor portal: a public site built from `content/`, `data/`, `prompts/`, `templates/`, and `assets/` by `scripts/build.py`. `_site/` is generated and ignored by git.

Agenda Mentor is a Freyja Labs project served at `mentor.freyjalabs.com` by the Cloudflare Worker `agenda-mentor`, static assets only (`wrangler.jsonc`). A git-connected Workers Build runs the build and `npx wrangler deploy` on every push to `main`; there is no GitHub Actions deploy, and the custom domain is attached in the Cloudflare dashboard (README, "Publish").

- Run `python scripts/build.py --check` after every edit and fix any error before committing.
- Freyja Labs is independent of its founders' universities: never name UCF, DRACO Lab, Idaho National Laboratory (INL), or another institution as an affiliation in anything the build publishes.
- The build writes `_headers` with a strict content security policy: no inline script or style, nothing loaded from another origin, and a form that never submits. Keep pages within it, and check new pages with `npx wrangler dev` and a browser console before committing.
- Templates link to `.../index.html`; the build rewrites those links to `.../`, the form Cloudflare serves without a redirect. The 404 page links from `site_url`'s root path because it is served at any depth.
- Everything the build publishes is public. Never add a real agenda, intake, CV, whiteboard photo, review, or tracker data; the tracker template ships fictional sample data only.
- Keep `schema/agenda.schema.json` section keys and `data/anatomy.yaml` keys identical; the build enforces it, and Facultory's Research Agenda tool uses the same keys.
- Prompt placeholders must be in `KNOWN_FIELDS` (`scripts/build.py`) and have a form field in `templates/prompts.html`.
- The schema's `intake` keys match `INTAKE_FIELDS` in `scripts/build.py` and Facultory's `INTAKE_KEYS`; the builder's **Download your answers** file must keep importing into Facultory's Research Agenda tool.
- Every statement about Facultory (`templates/partials/facultory.html`, the prompts handoff, the track, mentors, and about pages) must be true of the Research Agenda tool as shipped. Name no prices or offers; the signup page shows those. Keep the line saying this site and Facultory have the same author.
- Discipline profiles name funder types with examples and keep `verify_note`; do not state a program's current status as fact.
- Writing follows Mike's voice: direct and declarative, American English, Oxford commas, acronyms spelled out at first use, no "not X, but Y" constructions, sentence case.
- Design rules: no card grids; red (`--redpen`) is reserved for things that need verification; the Kalam hand face appears only inside the board drawing.
