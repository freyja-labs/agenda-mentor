# Contributing

Every change arrives as a pull request, and `python scripts/build.py --check` must pass before review.

## Writing conventions

- Direct, declarative sentences in American English, with Oxford commas.
- Spell out every acronym at first use on each page.
- No "not X, but Y" constructions and no inflated adjectives.
- Sentence case for headings and buttons.

## Discipline profiles

1. Copy the `general` entry in `data/disciplines.yaml` and give it a new `id`.
2. Fill in every field. Paraphrase official criteria, and link the official page in `academy.url`.
3. Name funder types with current examples. Programs change, so keep `verify_note` honest about what moves fastest.
4. Ask a senior colleague in the field (associate professor or above, with a record in the field's flagship venues) to read it. Put their name in `reviewed_by` and the date in `reviewed_on`. A profile without a reviewer shows a notice on the site.
5. Run the check, then open the pull request.

The freshness workflow flags any profile whose review is more than twelve months old.

## Prompts

A prompt change should name the failure it fixes and show an example of the failure. Keep the section names in `02-draft-agenda.md` stable: mentors compare agendas across a cohort by section. Placeholders must be one of the fields in `KNOWN_FIELDS` in `scripts/build.py`; add a field there and in the builder form together.

## Corrections

Open an issue with the page, what it says, what it should say, and a source.

## What never goes in this repository

Real agendas, intakes, CVs, whiteboard photos, red-team reviews, or trackers. The published site is public. Faculty keep their own work in private repositories created from `tracker-template/`.
