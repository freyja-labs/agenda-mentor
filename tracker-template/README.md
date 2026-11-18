# Research agenda tracker (template)

A GitHub-backed tracker for carrying out a research agenda. Plain YAML in `data/` is the single source of truth. Every push validates the data and rebuilds three outputs:

- `site/index.html`: a self-contained dashboard that opens from disk or any static host
- `site/calendar.ics`: gates, external dates, and open actions as a subscribable calendar
- `site/digest.md`: the weekly digest, posted as a GitHub issue every Monday so it reaches your inbox

The files in `data/` are **fictional sample data**. Replace them with the output of prompt 5 from the Agenda Mentor portal (`prompts/05-tracker-seed.md`).

## Set up

1. Create a new **private** repository and copy this folder's contents into it.
2. Replace the sample files in `data/` with your own, then set `repo.slug` in `data/agenda.yaml` to `owner/name` and `repo.published` to `true`, so the dashboard links each ID to its line on GitHub.
3. Run `pip install -r requirements.txt` and `python scripts/build.py --check`; fix anything it reports.
4. Push. Check that Actions are enabled (Settings, Actions); the first push runs the build workflow.
5. Give your mentor read access, so the digest and dashboard are shared without sending files.
6. Optional: set repository variable `DIGEST_MENTION` to your GitHub login so the Monday digest mentions you, and `TRACKER_TZ` to your time zone.

## Layout

| Path | What it holds |
|---|---|
| `data/agenda.yaml` | Settings, the agenda clock (month 0, the make-or-break date, the two target years), thrusts with their health, grand challenges, and the glossary |
| `data/milestones.yaml` | Gates toward the make-or-break result, plus community and recognition milestones |
| `data/actions.yaml` | Next actions with owner, due date, status, and a definition of done |
| `data/deadlines.yaml` | External dates, each with a confidence level and a source link |
| `data/funding.yaml`, `data/publications.yaml` | Pipelines, including adjacent work that competes for the same hours |
| `data/kpis.yaml` | The scoreboard: baselines from the record, then near and far targets |
| `data/risks.yaml`, `data/claims.yaml` | The risk register and the claims ledger |
| `data/decisions.yaml` | Decisions the agenda needs, in the order they will be asked |
| `scripts/build.py` | Validation and all three outputs |
| `scripts/agenda.py` | Command-line edits that keep comments and ordering |
| `scripts/protect.py` | Encrypts the dashboard for GitHub Pages (below) |

## Updating

The build validates on every push and fails on bad dates, unknown IDs, or bad status values.

```sh
python scripts/agenda.py status                       # overdue, due soon, decisions waiting
python scripts/agenda.py set A-004 done
python scripts/agenda.py set A-003 waiting --note "District reply expected Feb 10"
python scripts/agenda.py decide D-02 "Differentiate; invite them to the symposium"
python scripts/agenda.py add-action "Email the program officer" --due 2027-01-15 --thrust T1 --links F-02
python scripts/build.py && open site/index.html       # preview locally
```

Never delete an item; set `status: dropped` so the history stays. Keep IDs stable; they are the calendar identifiers, so renaming one duplicates its calendar entry.

## Calendar feed

Outlook and Google Calendar subscribe to a URL they can fetch without signing in. Pick one:

- **Secret gist.** Create a secret gist with a file named `calendar.ics`. Save a token with the `gist` scope as repository secret `GIST_TOKEN` and the gist's ID as repository variable `CAL_GIST_ID`. Each build overwrites the file; subscribe to `https://gist.githubusercontent.com/<you>/<gist-id>/raw/calendar.ics` and put that URL in `calendar.feed_url`. The URL is unlisted and needs no sign-in, so anyone who has it can read the event titles.
- **Cloudflare Pages.** Connect the private repository, build command `pip install -r requirements.txt && python scripts/build.py`, output `site`. Protect the site with Cloudflare Access and add a bypass rule for `/calendar.ics` only.
- **No hosting.** Download `calendar.ics` from the latest workflow run's `site` artifact and import it. Imports do not update; re-import after changes.

## Dashboard on GitHub Pages (password)

GitHub Pages sites are public even for private repositories, so the page that ships holds only ciphertext. `scripts/protect.py` encrypts the built dashboard with AES-256-GCM under a key derived from a passphrase (PBKDF2-SHA256, 600,000 iterations), and the browser decrypts it locally. The passphrase never leaves the browser, and `data.json`, `digest.md`, and `calendar.ics` never reach Pages.

1. Settings, Pages: set the source to "GitHub Actions".
2. Settings, Secrets and variables, Actions: add the secret `DASHBOARD_PASSWORD`, a passphrase of four or more random words. The script refuses anything shorter than 12 characters, so a missing or weak secret publishes nothing.
3. Under Variables, add `DEPLOY_PAGES` with the value `true`.
4. Actions, Build tracker, Run workflow. Every later push redeploys the page.

Anyone can download the encrypted page and guess passphrases offline, so the passphrase is the whole defense. The page keeps out casual visitors and search engines; it does not stop a determined adversary who can guess the passphrase. To change it, update the secret and rerun the workflow.

## Date confidence

`verified` checked against the organizer or funder · `reported` third-party listing · `derived` computed from a published rule · `expected` projected from last year · `record` from your CV or award documents. Replace `expected` dates as calls are released.
