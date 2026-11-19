---
title: About
description: Where the method comes from, what happens to what you type, and how to contribute.
nav: About
order: 8
---

## Where the method comes from

The section skeleton comes from a series of R&D agendas written for engineering faculty with an AI drafting assistant, a whiteboard session, and each faculty member's public CV. A red-team review of one of those agendas found the predictable failures listed on the [verification page](../verify/). The prompt chain here keeps the series' structure, so agendas stay comparable, and adds the checks that review showed were missing. The discipline profiles extend it beyond engineering: an education researcher gets the same skeleton with the National Academy of Education, AERA, and the field's own venues, funders, and standards of evidence.

## What happens to what you type

The prompt builder runs entirely in your browser. Nothing you type is sent anywhere; the page has no analytics and loads no third-party fonts or scripts. The builder keeps your entries in this browser's local storage so you can come back to them, and the Clear button removes them. The prompts themselves go wherever you paste them, under that service's terms; follow your institution's rules on which AI services may see unpublished work.

**Download your answers** saves a file to your computer. Nothing reaches Facultory until you import that file there yourself. Links to Facultory open its signup with this site named as the source, and they carry nothing you typed.

## Facultory

This site and [Facultory]({{facultory_signup}}), a hosted platform for faculty, have the same author. Facultory's Research Agenda tool keeps an agenda in the format this site publishes and gives a mentor a review link that needs no account. Everything on this site works without it.

## Contribute

The site is built from plain files in a GitHub repository, so improvements arrive as pull requests.

- **A discipline profile for your field.** Copy the `general` profile in `data/disciplines.yaml`, fill it in, and ask a senior colleague in the field to review it. The `reviewed_by` field records who did.
- **A correction.** Open an issue with the page, what it says, what it should say, and a source.
- **A prompt change.** Explain the failure it fixes, with an example.

`CONTRIBUTING.md` in the repository has the details, and `python scripts/build.py --check` runs the same checks the pull-request workflow runs.
