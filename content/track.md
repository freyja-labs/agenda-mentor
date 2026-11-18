---
title: Track the agenda
description: A tracker template that turns version 2 into a dashboard, a calendar feed, and a weekly digest from plain files on GitHub.
nav: Tracker
order: 7
---

An agenda that lives in a document gets read twice a year. The tracker keeps it in front of the faculty member every week. It is a small repository of plain YAML files: gates, actions, external dates, funding, publications, a scoreboard, risks, the claims ledger, and the decision log. Every push validates the files and rebuilds three outputs.

- **A dashboard**: one self-contained page that opens from disk or any static host.
- **A calendar feed**: gates, external dates, and open actions as a subscribable `.ics` file.
- **A weekly digest**: overdue and upcoming items, posted as a GitHub issue every Monday so it reaches the inbox.

The template is in [`tracker-template/`]({{repo_url}}/tree/main/tracker-template) in this repository, with fictional sample data.

## Set it up

1. Create a new **private** repository and copy the contents of `tracker-template/` into it.
2. Run [prompt 5](../prompts/#p05-tracker-seed) on version 2 of the agenda, and replace the sample files in `data/` with its output.
3. Run `python scripts/build.py --check`, fix anything it reports, and push. The first push runs the build workflow.
4. Give the mentor read access to the repository, so the digest and the dashboard are shared without sending files.

## Optional: the dashboard on GitHub Pages

GitHub Pages sites are public even for private repositories, so the template never publishes the dashboard as is. When you turn Pages on, `scripts/protect.py` encrypts the dashboard with a passphrase you store as a repository secret, and the browser decrypts it locally. The data files, the digest, and the calendar never reach Pages. The template's README has the steps and the limits of that protection.

## Everyday updates

```sh
python scripts/agenda.py status                    # overdue, due soon, decisions waiting
python scripts/agenda.py set A-004 done
python scripts/agenda.py decide D-03 "Collaborate on the benchmark"
python scripts/agenda.py add-action "Email the program officer" --due 2027-01-15 --thrust T1
python scripts/build.py                            # rebuild site/ locally
```

Never delete an item; set its status to `dropped`, so the history stays. IDs never change, because they double as calendar identifiers.

## Without GitHub

Faculty who would rather not run a repository can keep the same agenda, claims ledger, decisions, and gates in a hosted tool. The section keys and the ledger format match [`schema/agenda.schema.json`]({{repo_url}}/blob/main/schema/agenda.schema.json), so an agenda can move between the two.
