# Agenda Mentor

A mentorship portal for faculty building a five-year research agenda: a method that starts at a whiteboard, six prompts that draft and then red-team the agenda, discipline profiles that carry each field's conventions, a mentor guide with a review rubric, a verification checklist, and a tracker template that keeps the agenda in front of the faculty member every week.

The site is built from the plain files in this repository and published with GitHub Pages. The prompt builder runs in the visitor's browser; nothing typed into it is sent anywhere.

## Layout

| Path | What it holds |
|---|---|
| `prompts/` | The prompt chain, one Markdown file per step (`01` to `06`), plus `00-reconstructed.md`, the original single-pass format kept for reference |
| `data/disciplines.yaml` | Discipline profiles: engineering and computing, education research, engineering education, and a general profile |
| `data/stages.yaml`, `anatomy.yaml`, `rubric.yaml`, `sessions.yaml`, `checklist.yaml` | The path, the agenda's sections, the mentor rubric, the mentoring year, and the verification checklist |
| `schema/agenda.schema.json` | The agenda as JSON, with section keys that match `data/anatomy.yaml`; other tools use the same keys |
| `content/` | Page text in Markdown; `[[stages]]`-style markers pull in the data above |
| `templates/`, `assets/` | Jinja templates, the stylesheet, the builder script, and self-hosted fonts (SIL Open Font License) |
| `scripts/build.py` | Validation and the site build |
| `tracker-template/` | A copy-me tracker: YAML data in, a dashboard, a calendar feed, and a weekly digest issue out |

## Build locally

```sh
pip install -r requirements.txt
python scripts/build.py --check     # data, prompts, schema, and every internal link
python scripts/build.py             # writes _site/
python -m http.server -d _site 8000
```

The build fails on a missing profile field, an unknown prompt placeholder, unbalanced `{{#if}}` blocks, prompt numbering out of order, a schema that disagrees with `data/anatomy.yaml`, or a broken internal link.

## Publish

1. Settings, Pages: set the source to **GitHub Actions**.
2. Push to `main`. The `pages` workflow builds the site and deploys it.
3. Set `repo` in `config.yaml` if the repository is not `ucf-draco-mike/agenda-mentor`; the site links to its own source files there.

GitHub Pages sites are public, including those built from private repositories. Everything in `_site/` is meant to be public: the method, the prompts, and the profiles. Keep real agendas, intakes, and trackers in private repositories, never here.

## Workflows

- `pages.yml` builds and deploys on every push to `main`.
- `check.yml` runs the same validation on pull requests, and builds the tracker template against its sample data.
- `freshness.yml` runs on the first of each month and opens (or updates) one issue listing profiles that no senior colleague has reviewed in the last twelve months.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Discipline profiles are the most useful contribution: copy the general profile, fill it in with sources, and have a senior colleague in the field review it.
