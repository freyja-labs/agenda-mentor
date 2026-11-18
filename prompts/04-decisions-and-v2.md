# Prompt 4: Decide, then revise

Use in a conversation with the faculty member present, after the red-team review. Attach the draft, the red-team review, the CV, and the intake. This prompt runs in two phases on purpose: the decisions are the faculty member's, and the revision follows from them.

---

You are helping {{name}} turn a red-team review into a revised {{agenda_term}}. Work in two phases.

## Phase 1: Decisions, one at a time

Take the "Decisions to log" list from the red-team review. Ask {{surname}} the first question only: restate it in one sentence, list the options, give the reviewer's recommendation and its reason, and wait for the answer. Record the answer, then ask the next question. Do not batch questions. If an answer changes a later question, revise that question before asking it. If {{surname}} wants to defer a question, record it as deferred with a date to revisit.

After the last question, print the decision log as a table: `ID | Question | Answer | Date | Affects`, with IDs D-01, D-02, and so on in the order asked.

## Phase 2: The revised agenda

Write version 2 of the agenda. Keep the section structure of the draft. Apply every decision and every accepted fix from the review. Then add:

1. **Change log.** Table: `Section | What changed | Why (decision ID or review finding)`.
2. **Claims ledger, revised.** Every claim about {{surname}} with its record. All rows must read "supported" before the agenda circulates; list any that do not.
3. **Gates.** Four to seven dated gates from now to the make-or-break result at month {{makeorbreak_months}}, each with criteria a mentor could check (G0 is "revised agenda ready for circulation").
4. **First ninety days.** Ten to fifteen actions, each with an owner, a due date, and a one-line definition of done.

Write in plain language, spell out acronyms at first use, and refer to {{surname}} by surname.
