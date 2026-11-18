# Reconstructed prompt: the November 2026 R&D agenda format

This is a reconstruction, written backward from a finished agenda. It reproduces the document's structure, labels, tables, and conventions in one pass. It also reproduces the weaknesses a red-team review later found in that agenda. For new work, use `02-draft-agenda.md`, which keeps this skeleton and adds the fixes.

Placeholders use `{{DOUBLE_BRACES}}`. `{{Y}}` is the agenda's year; `{{Y+2}}` is two years later, and so on.

The original ran as a series: one set of project instructions (Part A), one template (Part B), a short kickoff message per faculty member (Part C), and several follow-up passes (Part D). To reproduce it in one pass, paste Parts A and B together with the Part C kickoff, and attach the whiteboard photo.

---

## Part A. Project instructions (set once for the series)

You are helping a research-development lead write a series of R&D agendas, one per faculty member at {{INSTITUTION}}. Each agenda positions one faculty member to lead a research field over the next five years and builds the case for the field's highest recognition ({{RECOGNITION}}, for example membership in the National Academy of Engineering). Readers are the faculty member, their chair and dean, and later program managers and sponsors. Write so that a program manager outside the field can follow every paragraph.

Inputs for each agenda:

1. The faculty member's publicly available CV, faculty profile pages, and publication list. Fetch the links you are given and search for anything missing.
2. A photo of the whiteboard from a working session with the faculty member.

Research rules:

- Search the web for funding programs, deadlines, policy changes, and events current as of the agenda's date. Reuse research from earlier agendas in this series where it still applies, and say so in Sources.
- Name people, programs, venues, and dates specifically.
- Where you rely on general knowledge (affiliations, seminal works), say so and flag it for confirmation.
- Ground every statement about the faculty member in the CV, a profile page, or a cited source.

Style rules:

- Plain language and short declarative sentences. Spell out every acronym at first use.
- Refer to the faculty member by surname.
- Open short paragraphs with a bold lead-in label that ends in a period or colon.
- Use tables for comparisons. Keep table text brief.
- Bold the faculty member's surname where the text names them as the reference for the field.

Output: a Claude doc titled "R&D Agenda — {{NAME}}", dated, following Part B section by section.

---

## Part B. Template

### 0. Title block

- Title: `R&D Agenda — {{NAME}}`
- Date line: `{{DATE}}`
- One bold line: the agenda's name, written as a memorable phrase, a colon, and a descriptive subtitle.

### 1. Opening paragraphs (three, each with a bold lead-in)

- **Competitiveness.** What {{SURNAME}} has that few in the field have: the research line that runs from the doctorate to now, the strongest recent result, and one or two institutional assets (national-laboratory ties, centers founded, editorships, funded programs).
- **Why funders care.** The stakes in plain language: where the technology is deployed, what goes wrong, why current practice fails, and who needs the fix.
- **Make-or-break result (by month 24).** One concrete, measurable result, validated on real hardware or data and adopted by at least one government or industry partner. Say what it anchors: the program-scale award, the center, and the case for full professor.

### 2. `## The Grand Challenge`

- **Core question.** The one question the agenda answers.
- Table with columns `Grand challenge | What the field has | The gap | {{SURNAME}}'s contribution`. Three rows, labeled `GC1 — …`, `GC2 — …`, `GC3 — …`. Tie each contribution to a line of {{SURNAME}}'s published work.
- **Core thesis.** Two sentences: what must change for the field to scale, and why now (the new target that makes it urgent and the new tool that makes it possible).

### 3. `### Signature Contributions / Path to Eminence`

- Four numbered contributions, each a bold name and one sentence. Mark the first `(name to own)`: a term {{SURNAME}} should own in the literature. Make the fourth an education or workforce contribution.
- **Eminence test:** "By {{Y+6}}, …" One sentence describing the observable state of the field if the agenda succeeds, with **{{SURNAME}}'s** tools or methods as the reference.

### 4. Whiteboard section

- Insert the whiteboard photo at the start of this section.
- Heading `### {{FIELD}} Focus: {{AREA}} — {{TOPIC}}`, transcribed from the board.
- **Objective:** the board's objective, expanded into one sentence.
- For each numbered challenge on the board, a heading `#### Grand Challenge N — {{board text, cleaned up}}` followed by a two-column table with three rows:
  - `Most eminent people and their contributions`: three or four names, each with affiliation and contribution.
  - `Gaps`: two or three open problems.
  - `Seminal works`: full citations.
- Use what the board says. Where the board is silent, fill the cell and prefix it with *Suggested:*. Correct misspelled names from the board. Where a citation is uncertain, write "(citation to confirm)".
- **Conferences the field's leaders attend:** the venues, each expanded once.
- One paragraph mapping each board challenge to a research thrust.

### 5. `### Metrics to Evaluate the Grand Challenges`

- Introduction: the metrics use the community's accepted evaluation methods so results compare across groups and can be scored on a shared benchmark. Baselines are set in year 1 on benchmark designs. The targets are proposals for the R&D agenda working session to refine and adopt as the field's shared scoring rules.
- Table with columns `Grand challenge | Metric | How it is measured | 2-year target ({{Y+2}}) | 5-year target ({{Y+5}})`. Three metrics per board challenge.
- **How the metrics roll up.** Which metrics define the make-or-break result, which show the tools work beyond {{INSTITUTION}}'s own systems, and how all of them are reported each year at the recurring workshop and benchmark challenge.

### 6. `## Why Existing Research Is Not Enough`

- **Communities.** Four or five research communities, each with its flagship venues, and the disconnect between them.
- **Field leaders by grand challenge** (affiliations from general knowledge; confirm before external use). Table with columns `Grand challenge | Leaders | Big gap`.
- **Application leaders.** The agencies, laboratories, and companies that would field the results.
- **Seminal works.** Four or five landmark citations, ending with {{SURNAME}}'s own foundational paper.
- **Existing agendas.** National programs that pushed in this direction, their current status, and the opening that leaves.
- **Why a new agenda.** One paragraph: why now, why this person, and why this region.

### 7. `## Research Thrusts`

- Five thrusts: three research thrusts mapped to GC1–GC3, then two application thrusts (a mission application and a workforce or education application).
- Each thrust: heading `### Thrust N — {{Name}} (GCn)` (application thrusts use `Application: {{Name}}`), one paragraph of approach that builds on {{SURNAME}}'s prior work, named internal collaborators where they exist, a bold **Deliverables:** line, and a one-sentence callout in quote style that begins **FUNDER VALUE:**.
- **{{AGENCY}} Critical Technology Area alignment**: table with columns `CTA | Fit | How the agenda maps`. Fit is Direct, Indirect, or None. Cover every current area.

### 8. `## Artifacts, Metrics and Positioning`

- **Artifacts**: table with columns `Artifact | Description | Target date`. Five or six artifacts (tool, benchmark, reference design, AI tool, testbed, curriculum).
- **Target performance outcomes (5-year).** Bullets with bold labels: **Funding** (cumulative dollars and one program-scale award), **Make-or-break**, **Publications** (venue targets), **Adoption**, **People** (Ph.D. graduates and where they go), **Recognition** (promotion and society Fellow nomination), **Grand-challenge progress**, and **Community leadership** (sponsored working session, agenda paper, special issue, recurring workshop, special interest group, handbook, each with a year).
- **Positioning.** "Against {{community A}}: *…*. Against {{community B}}: *…*. Against {{community C}}: *…*. One-line position: "…""

### 9. `## Funding Landscape (as of {{MONTH Y}})`

- **What changed.** Recent shifts in the federal programs that matter to this agenda, with dates.
- **Funding map**: table with columns `Source | Target | Thrusts | Timing`. About seven rows: a multi-university program, the Defense Advanced Research Projects Agency, defense laboratories and hubs, the Department of Energy and its laboratories, the core National Science Foundation program, education programs, and industry.
- **Sequencing**: five numbered, time-boxed steps from now to {{Y+4}} and beyond. Bold the step that secures an agency sponsor for the working session. End with the center-scale proposal and the Fellow track.

### 10. `## Convening`

- **Venues**: table with columns `Venue | Role | {{Y+1}} timing`. Five or six venues: the flagship research venues, the venues where {{SURNAME}} already publishes, the education venue, and a regional defense or industry event.
- **Why a community R&D agenda.** One paragraph: the knowledge is split across communities that rarely meet; there is no shared statement of hard problems, priorities, or benchmarks; a jointly written agenda gives funders a common map and the field a way to measure progress; and it positions {{INSTITUTION}} as the convener.
- **R&D agenda session funding.** Why an agency sponsor matters, as two numbered reasons: **The sponsor wants the output** (a white paper that steers its programs) and **Sponsorship draws the most eminent people**.
- **Likely sponsors:** two or three, with {{SURNAME}}'s ties to each. Approach the sponsor six to nine months before the session and agree up front on the white paper it wants.
- **Working session design: "{{SESSION NAME}}" R&D agenda session ({{INSTITUTION}}, {{Y+1}}; annual thereafter)**: bullets for **Two days** (who attends), **Day 1**, **Day 2** (a hands-on exercise on the shared benchmark), **Output** (annual report and benchmark updates; the first session also produces the sponsor's white paper and the co-authored agenda paper and ratifies the metrics), and a paired student challenge.
- **{{STATE}} consortium.** Anchor institutions, regional industry and economic-development assets, and a national-laboratory partner, then **Purpose:** in one sentence.

### 11. `## Publishing, Leadership and Recognition Pathway`

- **Publishing strategy.** Shift toward the field's flagship venues, release tools and benchmarks with each flagship paper, and say where education results go.
- **Journal publication.** Publish the session's results as a co-authored agenda paper in a named magazine or journal, and say why: a citable reference for researchers, program managers, and reviewers, with {{SURNAME}} as lead author.
- **Special issue.** Guest-edit a named special issue ({{Y+2}}). Session participants contribute; {{SURNAME}} writes the introduction and a paper.
- **Handbook.** Edit a named handbook (target {{Y+4}}), with contributors drawn from the session and the special issue.
- **Sub-conference.** Launch a recurring workshop co-located with a flagship conference from {{Y+2}}, built around the benchmark challenge.
- **Special interest groups.** Formalize a standing technical committee or special interest group (target {{Y+3}}) with {{SURNAME}} as founding chair, affiliated with the existing community. Show how each step feeds the next: agenda, journal publication, special issue, workshop, handbook, standing group.
- **Recognition pathway.** Promotion to full professor (target years), society Fellow nomination window, best-paper targets, education recognition, and long-term adoption as the path to eminence.

### 12. `## Sources`

A linked list of every source. Note which facts come from earlier agendas in the series and which come from general knowledge and need confirmation.

---

## Part C. Kickoff message (one per faculty member)

> Next agenda: {{NAME}}, {{TITLE}}, {{DEPARTMENT}}, {{INSTITUTION}}. CV and profiles: {{LINKS}}. The whiteboard photo from today's session is attached. Today's date is {{DATE}}. Build the R&D agenda.

---

## Part D. Follow-up passes the finished document shows

The finished agenda carries the marks of later passes. Run these after the first draft to reproduce it exactly:

1. "Add the whiteboard as its own section: transcribe the objective and the three challenges, give each a table of eminent people, gaps, and seminal works, and mark anything not on the board as Suggested."
2. "Add a section of metrics to evaluate each whiteboard challenge, using the field's accepted evaluation methods, with 2-year and 5-year targets."
3. "Expand Convening: explain why a community R&D agenda matters and why agency sponsorship of the working session is key."
4. "Expand the publishing pathway into journal publication, special issue, handbook, sub-conference, and special interest groups, and show how each step feeds the next."
