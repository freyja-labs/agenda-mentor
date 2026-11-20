# Agenda Mentor

A mentorship portal for faculty building a five-year research agenda: a method that starts at a whiteboard, six prompts that draft and then red-team the agenda, discipline profiles that carry each field's conventions, a mentor guide with a review rubric, a verification checklist, and a tracker template that keeps the agenda in front of the faculty member every week.

Agenda Mentor is a [Freyja Labs](https://freyjalabs.com) project, served at **https://mentor.freyjalabs.com** by Cloudflare. The site is built from the plain files in this repository. The prompt builder runs in the visitor's browser; nothing typed into it is sent anywhere.

## Layout

| Path | What it holds |
|---|---|
| `prompts/` | The prompt chain, one Markdown file per step (`01` to `06`), plus `00-reconstructed.md`, the original single-pass format kept for reference |
| `data/disciplines.yaml` | Discipline profiles: engineering and computing, education research, engineering education, and a general profile |
| `data/stages.yaml`, `anatomy.yaml`, `rubric.yaml`, `sessions.yaml`, `checklist.yaml` | The path, the agenda's sections, the mentor rubric, the mentoring year, and the verification checklist |
| `schema/agenda.schema.json` | The agenda as JSON, with section keys that match `data/anatomy.yaml`; other tools use the same keys |
| `content/` | Page text in Markdown; `[[stages]]`-style markers pull in the data above |
| `templates/`, `assets/` | Jinja templates, the home page walkthrough, the typed board, the stylesheet, the builder, walkthrough, and typed board scripts, and self-hosted fonts (SIL Open Font License) |
| `scripts/build.py` | Validation and the site build |
| `tracker-template/` | A copy-me tracker: YAML data in, a dashboard, a calendar feed, and a weekly digest issue out |

## Build locally

```sh
pip install -r requirements.txt
python scripts/build.py --check     # data, prompts, schema, and every internal link
python scripts/build.py             # writes _site/
npx wrangler dev                    # serves _site/ the way Cloudflare does, with _headers and the 404 page
```

`python -m http.server -d _site 8000` also works for a quick look, without the response headers or the 404 page.

The build fails on a missing profile field, an unknown prompt placeholder, unbalanced `{{#if}}` blocks, prompt numbering out of order, a schema that disagrees with `data/anatomy.yaml` or with the builder's intake fields, a malformed `facultory` block in `config.yaml`, or a broken internal link.

## Publish

The site is the Cloudflare Worker `agenda-mentor`, static assets only (`wrangler.jsonc`), deployed the way `freyja-labs/freyjalabs-site` is: a git-connected Workers Build runs on every push to `main`. There is no GitHub Actions deploy.

One-time setup, in the Freyja Labs Cloudflare account:

1. **Workers & Pages → Create → Import a repository**, and choose `freyja-labs/agenda-mentor`.
2. Build settings:
   - Build command: `pip install -r requirements.txt && python scripts/build.py --out _site`
   - Deploy command: `npx wrangler deploy`
   - Root directory: `/`, production branch: `main`. `.python-version` pins Python 3.12, the version CI uses.
3. **Settings → Domains & Routes → Add custom domain**: `mentor.freyjalabs.com`. Cloudflare creates the proxied DNS record and the certificate.
4. Leave Cloudflare Web Analytics' automatic setup off for this hostname. The About page says the site runs no analytics, and the content security policy in `_headers` blocks the injected script.

The build runs every check before it writes anything, so a commit that fails `--check` never deploys. Builds of other branches get a preview address on `workers.dev`; the canonical links on every page point search engines at `mentor.freyjalabs.com`.

`config.yaml` holds what changes per deployment:

- `site_url`: the address the site is served at. Canonical links, `sitemap.xml`, the 404 page, and the schema's `$id` are built from it, and the build checks that the schema agrees.
- `publisher`: named in the footer and on the About page.
- `repo`: the GitHub repository the site links to for its source files and issues.
- `facultory`: where the "keep it in Facultory" links point: the plan the signup form selects, the label it records under "How did you hear about Facultory?", and the page that opens after sign-in. The build checks each value.

Everything in `_site/` is public: the method, the prompts, and the profiles. Keep real agendas, intakes, and trackers in private repositories, never here.

## Workflows

- `check.yml` runs the build's validation on pull requests, and builds the tracker template against its sample data.
- `freshness.yml` runs on the first of each month and opens (or updates) one issue listing profiles that no senior colleague has reviewed in the last twelve months.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Discipline profiles are the most useful contribution: copy the general profile, fill it in with sources, and have a senior colleague in the field review it.
