# Prompt 5: Seed the tracker

Use on the revised agenda from prompt 4. The output fills the `data/` folder of the tracker template (`tracker-template/` in this repository), which builds a dashboard, a calendar feed, and a weekly digest from plain YAML.

---

Convert the attached revised {{agenda_term}} for {{name}}, its decision log, and its red-team review into the tracker's YAML files. Today is {{date}}. Output one fenced code block per file, labeled with its path. Use only the fields listed. Dates are ISO (`YYYY-MM-DD`). IDs are stable and sequential; they become calendar identifiers, so never reuse one.

**`data/agenda.yaml`**: `title`, `subtitle`, `owner` ({{surname}}), `source_doc`, `timezone`, `clock` (`month0`: the first day of this month; `horizon_months`: {{makeorbreak_months}}; `makeorbreak_due`; `target_years`: the two KPI target years, {{year_plus_2}} and {{year_plus_5}}), `repo` (`slug`, `branch`, `published: false`), `calendar` (`name`, `feed_url: ""`), `thrusts` (each: `id` such as T1, T2, T3, AL, BI, X; `name`; `challenge`; `health`: one of on_track, at_risk, off_track, not_started, done; `where`: one or two sentences on current state with evidence; `next`; `origin`; `people`: list), `grand_challenges` (each: `id`, `name`, `science_question`), and `glossary` (each: `[term, expansion]` for every acronym the dashboard will show).

**`data/milestones.yaml`**: the gates G0–G6 and the community and recognition milestones. Fields: `id`, `title`, `date`, `date_precision` (day, month, or year), `track` (gate, community, recognition), `status` (not_started, open, in_progress, done, at_risk, missed, dropped), `thrusts`, `criteria` (list), `note`.

**`data/actions.yaml`**: the first-ninety-days actions. Fields: `id` (A-001…), `title`, `due`, `thrust` (list), `owner`, `status` (open, in_progress, waiting, blocked, done, dropped), `priority` (high, normal, low), `done_when`, `links` (IDs).

**`data/deadlines.yaml`**: every external date. Fields: `id` (E-001…), `title`, `date`, optional `time` (HH:MM) and `tz`, `kind` (deadline, event, award_end), `confidence` (verified, reported, derived, expected, record), `thrust`, `source` (a URL; required), `links`, `status` (tracking, pass), `note`.

**`data/funding.yaml`**: current awards and the pipeline. Fields: `id` (F-01…), `title`, `sponsor`, `amount_k`, `share_k`, `start`, `end`, `stage` (idea, shaping, submitted, pending, active, ended, declined, pass), `thrust`, `core` (true or false), `next_date`, `next_step`, `source`, `note`.

**`data/publications.yaml`**: Fields: `id` (P-01…), `title`, `venue`, `target_date`, `stage` (planned, drafting, submitted, revision, accepted, published, retarget), `flagship` (true or false), `thrust`, `core`, `links`, `note`.

**`data/kpis.yaml`**: the scoreboard. Fields: `id` (K-01…), `group` (outcome, science, people), `title`, `definition`, `unit` (count, usd_k, ratio, percent, text), `direction` (up, down), `baseline`, `baseline_note`, `current`, `as_of`, `target_near`, `target_far`.

**`data/risks.yaml`**: Fields: `id` (R-01…), `title`, `impact` (1–5), `likelihood` (1–5), `thrust`, `owner`, `mitigation`, `trigger`, `status` (open, watching, mitigated, closed), `links`.

**`data/claims.yaml`**: the claims ledger. Fields: `id` (CL-01…), `claim`, `record`, `fix`, `severity` (high, medium, low), `status` (open, fixed, accepted), `note`.

**`data/decisions.yaml`**: the decision log. Fields: `id` (D-01…), `order`, `question`, `status` (open, asked, decided, deferred), `options` (list), `recommendation`, `answer`, `asked_on`, `decided_on`, `links`.

After the files, list anything in the agenda you could not place, and any ID referenced in a `links` field that does not exist.
