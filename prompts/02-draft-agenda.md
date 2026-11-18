# Prompt 2: Draft the research agenda

Use after the whiteboard session and after the faculty member has confirmed the transcription from prompt 1. Attach the current CV (the faculty member's own file, not a public bio) and the whiteboard photo. The portal's prompt builder fills every `{{placeholder}}` and pastes in the discipline profile; to fill it by hand, replace each placeholder and delete any `{{#if}}` block you have nothing for.

---

You are drafting a five-year {{agenda_term}} for {{name}}, {{title}} in {{department}} at {{institution}}. The draft is a coaching document. {{name}}'s mentor{{#if mentor}} ({{mentor}}){{/if}} will review it with {{surname}}, a red-team pass will test it, and only a revised version will circulate. Readers of the revised version will include the department chair and dean, program officers, and senior people in the field, so write for a reader outside the specialty.

The agenda has two jobs. First, it states the hard problems in {{field}} that {{surname}} can lead the field on, and a credible five-year plan to make progress. Second, it lays out the path from {{surname}}'s current career stage ({{career_stage}}) toward the field's highest recognition. The discipline profile below names that recognition and the steps toward it.

## Inputs

1. **Current CV** (attached). This is the record. Every statement about {{surname}} must trace to it or to the intake below.
2. **Whiteboard transcription** (confirmed by {{surname}}):

{{whiteboard}}

3. **Intake** (from {{surname}}):
   - What {{surname}} wants to be known for: {{wants}}
   - Current funding, with end dates: {{funding}}
   - People (students, postdocs, staff) and what they work on: {{people}}
   - Teaching and service load: {{load}}
   - Institutional context (clusters, centers, partners, regional assets): {{context}}
   {{#if constraints}}- Constraints (names, affiliations, or sponsors to leave out): {{constraints}}{{/if}}
{{#if series}}
4. **Shared landscape notes** from earlier agendas in this cohort (refresh anything time-sensitive before using it):

{{series}}
{{/if}}

## Discipline profile

{{discipline_profile}}

## Rules

**Evidence.**
- Ground every claim about {{surname}} in the CV or the intake. Use present tense only for work with a current end date; describe ended awards, appointments, and programs in the past tense with their dates.
- Keep a claims ledger as you write (section 13). Every sentence that describes {{surname}}'s record, assets, or relationships gets a row.
- Never imply a collaboration, partnership, or sponsor relationship that the CV or intake does not show. Where one would help, propose it as an action.

**Gaps.** Before you say the field lacks something, search for commercial products, recent surveys or systematization papers, funded programs, and the two or three academic groups closest to the claim. State the gap as narrowly as that search supports, and name the nearest work beside it.

**Record versus target.** Report the baseline from the CV first (for example, papers in the field's flagship venues in the last five years), then the target. Never write a target as if it were already true.

**One taxonomy.** Grand challenges GC1–GC3 are field-level problems. The numbered items on the whiteboard become science questions S1–S3, each nested under one grand challenge. Never reuse a label.

**Capacity.** Use the intake's load. Plan at most three research thrusts plus an application lens and a broader-impacts layer. Add a thrust only when the intake shows money or people for it. Gate community-building artifacts (working session, special issue, workshop, handbook, standing group) on two events: a committed sponsor and one accepted paper in a flagship venue.

**Dates.** Search for every external date (deadlines, programs, events). Give each one a confidence level: `verified` (checked against the organizer or funder), `reported` (third-party listing), `derived` (computed from a published rule), `expected` (projected from last year), or `record` (from the CV or award documents). Never mark a date verified without opening the organizer's or funder's page.

**People.** For field leaders, give name, current affiliation, and contribution. Mark affiliations you did not verify with "(confirm)". Correct misspelled names from the whiteboard and note the correction.

**Citations.** Give full citations with a DOI or stable URL. Write "(citation to confirm)" for any you could not resolve. Prefix anything you supplied that the whiteboard did not with *Suggested:*.

**Style.** Plain language and short declarative sentences. Spell out every acronym at first use. Refer to {{surname}} by surname. Open short paragraphs with a bold lead-in label. Use tables for comparisons. American English, Oxford commas.

## Output

A document titled "{{agenda_title_prefix}} — {{name}}", dated {{date}}, with the sections below in this order. Keep the section names, so a mentor can compare agendas across a cohort.

### 0. Title block
The title, the date, and one bold line: the agenda's name as a memorable phrase, a colon, and a descriptive subtitle.

### 1. Opening
- **Competitiveness.** What {{surname}} has that few in the field have: the research line from the doctorate to now, the strongest recent result, and the institutional assets, each with its evidence.
- **Why funders care.** The stakes in plain language: where the problem shows up, what goes wrong, why current practice fails, and who needs the fix.
- **Make-or-break result (by month {{makeorbreak_months}}).** One concrete, measurable result, using the profile's make-or-break archetypes. Then an **Engine check**: the money, people, data, code, instruments, or partners that exist today, and what must exist by month 6 and month 12 for the result to land. If nothing exists yet, say so.

### 2. The Grand Challenge
- **Core question.**
- Table: `Grand challenge | What the field has (nearest work) | The gap | {{surname}}'s contribution`. Rows GC1–GC3. Tie each contribution to a line of {{surname}}'s published or funded work.
- **Core thesis.** Two sentences: what must change for the field to move, and why now.

### 3. Signature Contributions / Path to Recognition
- Four numbered contributions, each a bold name and one sentence. Mark the first `(name to own)`, and check by search that no product, program, or paper already owns the name. Make one an education, workforce, or practice contribution.
- **Recognition test:** "By {{year_plus_6}}, …" One observable state of the field if the agenda succeeds.

### 4. {{field}} Focus (from the whiteboard)
- Heading from the board's field, area, and topic.
- **Objective:** the board's objective in one sentence.
- For each science question S1–S3: a heading `S1 — …` naming its parent grand challenge, then a two-column table with rows `Most eminent people and their contributions`, `Gaps`, and `Seminal works`.
- **Where the field's leaders meet:** the venues, each expanded once.
- One paragraph mapping S1–S3 to the thrusts.

### 5. Metrics to Evaluate the Grand Challenges
- One sentence on the community's accepted evaluation methods, from the profile's metric conventions.
- Table: `Question | Metric | Definition (test, statistic, unit, baseline, budget) | Baseline (year 1) | {{year_plus_2}} target | {{year_plus_5}} target`. Two or three metrics per science question. A metric without a definition is not finished.
- **How the metrics roll up.** Which metrics define the make-or-break result and which show the work generalizes.

### 6. Why Existing Research Is Not Enough
- **Communities.** The communities that hold pieces of the problem, with their venues, and the disconnect between them.
- **Field leaders and nearest groups.** Table: `Grand challenge | Leaders (affiliation) | Nearest group to {{surname}} | Collaborate or differentiate? | Big gap`. Put the collaborate-or-differentiate call in section 14 as an open decision.
- **Application leaders.** The organizations that would use the results (see the profile).
- **Seminal works.** Four or five landmark citations.
- **Existing agendas.** National programs, consensus reports, or roadmaps that pushed in this direction, their status, and the opening that leaves.
- **Why a new agenda.** Why now, why {{surname}}, why here.

### 7. Research Thrusts
- Up to three research thrusts (mapped to GC1–GC3), then an application lens and a broader-impacts layer.
- Each: a heading, one paragraph of approach that builds on {{surname}}'s work, the people who will do it (from the intake, or "to recruit"), a bold **Deliverables:** line, and a one-sentence callout in quote style that begins **FUNDER VALUE:**.
- **Alignment:** a table against the profile's alignment frameworks: `Priority | Fit (Direct, Indirect, None) | How the agenda maps`.

### 8. Artifacts, Outcomes, and Positioning
- **Artifacts:** `Artifact | Description | Target date`.
- **Target outcomes ({{horizon_years}}-year).** For each of Funding, Make-or-break, Publications, Adoption, People, Recognition, Grand-challenge progress, and Community leadership: the baseline from the record, then the target.
- **Positioning.** Against each neighboring community, one italic phrase; then a one-line position.

### 9. Funding Landscape (as of {{month_year}})
- **What changed.** Recent shifts that matter, with dates and sources.
- **Funding map:** `Source | Program | Thrusts | Next date | Confidence | Source link`. Use the profile's funder types; include early-career programs that fit {{career_stage}}.
- **Sequencing:** five time-boxed steps from now to {{year_plus_5}}.

### 10. Convening
- **Venues:** `Venue | Role | Next date | Confidence`.
- **Why a community agenda.** One paragraph.
- **Sponsor.** Likely sponsors from the profile's convening forms, with {{surname}}'s existing ties to each. Approach six to nine months ahead and agree on the report the sponsor wants.
- **Working session design.** Two days, who attends, what each day does, and the outputs. State the gate: the session waits for a sponsor and a flagship acceptance.
- **Regional partners.** Start with one specific joint project with the closest regional group. A consortium is a later decision; log it in section 14.

### 11. Publishing, Leadership, and Recognition Pathway
- **Publishing strategy.** From the record's baseline to the flagship venues in the profile, with a venue plan by year.
- **The community cycle.** The profile's sequence (agenda paper, special issue, recurring workshop or symposium, handbook or edited volume, standing group), each with a year and its gate. Show how each step feeds the next.
- **Recognition pathway.** The profile's ladder from {{career_stage}}: next milestone, its timing, and what evidence it needs.

### 12. Capacity
Hours per week the plan needs against the intake's load, what {{surname}} would hand off or decline, and the protected research time the plan assumes.

### 13. Claims ledger
Table: `Claim (as written above) | Record (CV entry or intake line) | Tense check | Status (supported, needs fix, unsupported)`. Include every claim about {{surname}}'s record, assets, collaborators, and partners.

### 14. Open decisions
Numbered questions {{surname}} must answer before the agenda circulates, in the order to ask them. Each with two or three options and your recommendation. These are asked one at a time in the next step.

### 15. Sources
Every source, linked. Mark general-knowledge items "(confirm)" and give each date its confidence level.
