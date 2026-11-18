#!/usr/bin/env python3
"""Build the R&D agenda tracker: validate data/*.yaml, then write
site/index.html (self-contained dashboard), site/data.json, site/calendar.ics,
and site/digest.md (the weekly digest body).

Usage:
    python scripts/build.py                 # validate and build into site/
    python scripts/build.py --check         # validate only (CI gate)
    python scripts/build.py --today 2027-01-04 --digest-only
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OWNER = "Owner"   # replaced by agenda.yaml `owner` when the data loads
DATA = ROOT / "data"
TEMPLATE = ROOT / "site_src" / "index.template.html"

LIST_FILES = {
    "milestones": "milestones.yaml",
    "actions": "actions.yaml",
    "deadlines": "deadlines.yaml",
    "funding": "funding.yaml",
    "publications": "publications.yaml",
    "risks": "risks.yaml",
    "decisions": "decisions.yaml",
    "kpis": "kpis.yaml",
    "claims": "claims.yaml",
}

ENUMS = {
    "health": {"on_track", "at_risk", "off_track", "not_started", "done"},
    "milestones.status": {"not_started", "open", "in_progress", "done", "at_risk", "missed", "dropped"},
    "milestones.track": {"gate", "community", "recognition"},
    "milestones.date_precision": {"day", "month", "year"},
    "actions.status": {"open", "in_progress", "waiting", "blocked", "done", "dropped"},
    "actions.priority": {"high", "normal", "low"},
    "deadlines.kind": {"deadline", "event", "award_end"},
    "deadlines.confidence": {"verified", "reported", "derived", "expected", "record"},
    "deadlines.date_precision": {"day", "approx"},
    "deadlines.status": {"tracking", "pass"},
    "funding.stage": {"idea", "shaping", "submitted", "pending", "active", "ended", "declined", "pass"},
    "publications.stage": {"planned", "drafting", "submitted", "revision", "accepted", "published", "retarget"},
    "risks.status": {"open", "watching", "mitigated", "closed"},
    "decisions.status": {"open", "asked", "decided", "deferred"},
    "kpis.group": {"outcome", "science", "people"},
    "kpis.unit": {"count", "usd_k", "ratio", "percent", "text"},
    "kpis.direction": {"up", "down"},
    "claims.status": {"open", "fixed", "accepted"},
    "claims.severity": {"high", "medium", "low"},
}

REQUIRED = {
    "milestones": ["id", "title", "date", "track", "status"],
    "actions": ["id", "title", "due", "thrust", "status"],
    "deadlines": ["id", "title", "date", "kind", "confidence", "source"],
    "funding": ["id", "title", "sponsor", "stage", "thrust"],
    "publications": ["id", "title", "venue", "stage", "thrust"],
    "risks": ["id", "title", "impact", "likelihood", "mitigation", "status"],
    "decisions": ["id", "question", "status"],
    "kpis": ["id", "title", "group", "unit", "direction"],
    "claims": ["id", "claim", "record", "fix", "status"],
}

ID_LINE = re.compile(r"^\s*-\s+id:\s*[\"']?([A-Za-z0-9_-]+)[\"']?\s*$")


# --------------------------------------------------------------------------- load

def load(path: Path):
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    lines = {}
    for n, line in enumerate(text.splitlines(), start=1):
        m = ID_LINE.match(line)
        if m:
            lines[m.group(1)] = n
    return data, lines


def iso(v):
    if isinstance(v, (dt.date, dt.datetime)):
        return v.isoformat()
    return v


def normalize(obj):
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    return iso(obj)


def as_date(v) -> dt.date | None:
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return dt.date.fromisoformat(str(v))


def load_all():
    global DEFAULT_OWNER
    agenda, _ = load(DATA / "agenda.yaml")
    DEFAULT_OWNER = agenda.get("owner") or DEFAULT_OWNER
    bundle = {"agenda": agenda}
    index = {}
    for key, fname in LIST_FILES.items():
        items, lines = load(DATA / fname)
        bundle[key] = items or []
        for item_id, line in lines.items():
            index[item_id] = {"file": f"data/{fname}", "line": line}
    agenda_text = (DATA / "agenda.yaml").read_text(encoding="utf-8")
    for n, line in enumerate(agenda_text.splitlines(), start=1):
        m = ID_LINE.match(line)
        if m:
            index.setdefault(m.group(1), {"file": "data/agenda.yaml", "line": n})
    return bundle, index


# --------------------------------------------------------------------------- validate

def validate(bundle) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    agenda = bundle["agenda"]
    thrust_ids = {t["id"] for t in agenda.get("thrusts", [])}
    for t in agenda.get("thrusts", []):
        if t.get("health") not in ENUMS["health"]:
            errors.append(f"agenda.yaml thrust {t.get('id')}: health '{t.get('health')}' not in {sorted(ENUMS['health'])}")
    for key in ("month0", "makeorbreak_due"):
        try:
            as_date(agenda["clock"][key])
        except Exception:
            errors.append(f"agenda.yaml clock.{key} is not an ISO date")
    years = agenda.get("clock", {}).get("target_years")
    if not (isinstance(years, list) and len(years) == 2 and all(isinstance(y, int) for y in years) and years[0] < years[1]):
        errors.append("agenda.yaml clock.target_years must be two increasing years, for example [2028, 2031]")
    for g in agenda.get("glossary", []) or []:
        if not (isinstance(g, list) and len(g) == 2):
            errors.append(f"agenda.yaml glossary entry {g!r} must be [term, expansion]")

    seen = {}
    for key in LIST_FILES:
        items = bundle[key]
        if not isinstance(items, list):
            errors.append(f"{LIST_FILES[key]} must be a YAML list")
            continue
        for i, item in enumerate(items):
            where = f"{LIST_FILES[key]} item {i + 1}"
            if not isinstance(item, dict):
                errors.append(f"{where}: not a mapping")
                continue
            for field in REQUIRED[key]:
                if item.get(field) in (None, ""):
                    errors.append(f"{where} ({item.get('id', '?')}): missing '{field}'")
            iid = item.get("id")
            if iid in seen:
                errors.append(f"duplicate id {iid} in {LIST_FILES[key]} and {seen[iid]}")
            seen[iid] = LIST_FILES[key]
            for field, value in item.items():
                enum = ENUMS.get(f"{key}.{field}")
                if enum and value is not None and value not in enum:
                    errors.append(f"{where} ({iid}): {field} '{value}' not in {sorted(enum)}")
            for field in ("date", "due", "end", "start", "target_date", "next_date", "asked_on", "decided_on", "as_of"):
                if field in item and item[field] not in (None, ""):
                    try:
                        as_date(item[field])
                    except Exception:
                        errors.append(f"{where} ({iid}): {field} '{item[field]}' is not an ISO date")
            for t in item.get("thrust", []) or []:
                if t not in thrust_ids:
                    errors.append(f"{where} ({iid}): unknown thrust '{t}'")
            if key == "risks":
                for f in ("impact", "likelihood"):
                    if not isinstance(item.get(f), int) or not 1 <= item[f] <= 5:
                        errors.append(f"{where} ({iid}): {f} must be an integer 1-5")
            if key == "deadlines" and item.get("time"):
                if not re.fullmatch(r"\d{2}:\d{2}", str(item["time"])):
                    errors.append(f"{where} ({iid}): time must be HH:MM")
    all_ids = set(seen) | thrust_ids
    for key in LIST_FILES:
        for item in bundle[key]:
            for link in item.get("links", []) or []:
                if link not in all_ids:
                    warnings.append(f"{item.get('id')}: link '{link}' does not match any id")
    return errors, warnings


# --------------------------------------------------------------------------- calendar

def ics_escape(s: str) -> str:
    return (str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n"))


def fold(line: str) -> str:
    out, cur, limit = [], "", 75
    for ch in line:
        if len((cur + ch).encode("utf-8")) > limit:
            out.append(cur)
            cur, limit = ch, 74
        else:
            cur += ch
    out.append(cur)
    return "\r\n ".join(out)


def edit_url(agenda, index, item_id):
    repo = agenda.get("repo", {})
    if not repo.get("published") or item_id not in index:
        return None
    loc = index[item_id]
    return f"https://github.com/{repo['slug']}/blob/{repo.get('branch', 'main')}/{loc['file']}#L{loc['line']}"


def calendar_events(bundle, index):
    agenda = bundle["agenda"]
    tz_default = agenda.get("timezone", "America/New_York")
    events = []

    for d in bundle["deadlines"]:
        approx = d.get("date_precision") == "approx"
        passed = d.get("status") == "pass"   # kept for the record; no reminders
        title = d["title"] + (" (approx.)" if approx and "expected" not in d["title"] else "") + (" (pass)" if passed else "")
        desc = [f"Confidence: {d['confidence']}", f"Source: {d['source']}"]
        if d.get("note"):
            desc.append(d["note"])
        if d.get("links"):
            desc.append("Linked: " + ", ".join(d["links"]))
        ev = {
            "uid": d["id"], "summary": f"[{'Event' if d['kind'] == 'event' else 'Deadline'}] {title}",
            "start": as_date(d["date"]), "end": as_date(d.get("end")) or as_date(d["date"]),
            "time": d.get("time"), "tz": d.get("tz", tz_default),
            "categories": ["External", *d.get("thrust", [])],
            "description": "\n".join(desc),
            "url": d["source"] if str(d["source"]).startswith("http") else None,
            "alarms": ["-P7D", "-P1D"] if d["kind"] == "deadline" and not approx and not passed else [],
        }
        events.append(ev)

    for m in bundle["milestones"]:
        if m.get("date_precision", "day") != "day" or m["status"] in ("done", "dropped"):
            continue
        crit = "\n".join(f"- {c}" for c in m.get("criteria", []))
        events.append({
            "uid": m["id"], "summary": f"[Gate {m['id']}] {m['title']}",
            "start": as_date(m["date"]), "end": as_date(m["date"]), "time": None, "tz": tz_default,
            "categories": ["Gate", *m.get("thrusts", [])],
            "description": f"Status: {m['status']}\nWhat must be true:\n{crit}" + (f"\nNote: {m['note']}" if m.get("note") else ""),
            "url": edit_url(agenda, index, m["id"]), "alarms": ["-P7D", "-P1D"],
        })

    for a in bundle["actions"]:
        if a["status"] in ("done", "dropped"):
            continue
        desc = [f"Owner: {a.get('owner', DEFAULT_OWNER)}", f"Status: {a['status']}", f"Done when: {a.get('done_when', '')}"]
        if a.get("note"):
            desc.append(a["note"])
        if a.get("links"):
            desc.append("Linked: " + ", ".join(a["links"]))
        events.append({
            "uid": a["id"], "summary": f"[Action {a['id']}] {a['title']}",
            "start": as_date(a["due"]), "end": as_date(a["due"]), "time": None, "tz": tz_default,
            "categories": ["Action", *a.get("thrust", [])],
            "description": "\n".join(desc), "url": edit_url(agenda, index, a["id"]),
            "alarms": ["-P1D"] if a.get("priority") == "high" else [],
        })
    return events


def build_ics(bundle, index, now_utc: dt.datetime) -> str:
    agenda = bundle["agenda"]
    cal_name = agenda.get("calendar", {}).get("name", "R&D agenda")
    stamp = now_utc.strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//rd-agenda//tracker//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        f"X-WR-CALNAME:{ics_escape(cal_name)}",
        f"X-WR-CALDESC:{ics_escape('Gates, external deadlines, and open actions from the R&D agenda tracker')}",
        f"X-WR-TIMEZONE:{agenda.get('timezone', 'America/New_York')}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H",
    ]
    for ev in calendar_events(bundle, index):
        lines += ["BEGIN:VEVENT", f"UID:{ev['uid']}@rd-agenda.tracker", f"DTSTAMP:{stamp}"]
        if ev["time"]:
            hh, mm = (int(x) for x in ev["time"].split(":"))
            local = dt.datetime.combine(ev["start"], dt.time(hh, mm), tzinfo=ZoneInfo(ev["tz"]))
            start = local.astimezone(dt.timezone.utc)
            end = start + dt.timedelta(minutes=15)
            lines += [f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}", f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}"]
        else:
            lines += [f"DTSTART;VALUE=DATE:{ev['start'].strftime('%Y%m%d')}",
                      f"DTEND;VALUE=DATE:{(ev['end'] + dt.timedelta(days=1)).strftime('%Y%m%d')}"]
        lines += [f"SUMMARY:{ics_escape(ev['summary'])}", f"DESCRIPTION:{ics_escape(ev['description'])}",
                  f"CATEGORIES:{','.join(ics_escape(c) for c in ev['categories'])}", "TRANSP:TRANSPARENT"]
        if ev.get("url"):
            lines.append(f"URL:{ev['url']}")
        for trig in ev["alarms"]:
            lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{ics_escape(ev['summary'])}",
                      f"TRIGGER:{trig}", "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


# --------------------------------------------------------------------------- digest

def build_digest(bundle, index, today: dt.date) -> str:
    agenda = bundle["agenda"]
    month0 = as_date(agenda["clock"]["month0"])
    due = as_date(agenda["clock"]["makeorbreak_due"])
    months = (today.year - month0.year) * 12 + (today.month - month0.month)
    horizon = today + dt.timedelta(days=14)
    open_actions = [a for a in bundle["actions"] if a["status"] not in ("done", "dropped")]
    overdue = sorted((a for a in open_actions if as_date(a["due"]) < today), key=lambda a: as_date(a["due"]))
    soon = sorted((a for a in open_actions if today <= as_date(a["due"]) <= horizon), key=lambda a: as_date(a["due"]))
    ext = sorted((d for d in bundle["deadlines"] if d.get("status") != "pass"
                  and today <= as_date(d["date"]) <= today + dt.timedelta(days=30)),
                 key=lambda d: as_date(d["date"]))
    gates = sorted((m for m in bundle["milestones"] if m["track"] == "gate" and m["status"] not in ("done", "dropped")
                    and as_date(m["date"]) >= today), key=lambda m: as_date(m["date"]))[:2]
    decisions = sorted((d for d in bundle["decisions"] if d["status"] in ("open", "asked")), key=lambda d: d.get("order", 99))

    def ref(item_id):
        url = edit_url(agenda, index, item_id)
        return f"[{item_id}]({url})" if url else item_id

    out = [f"## Week of {today.isoformat()} · month {months} of {agenda['clock']['horizon_months']}",
           f"Make-or-break due {due.isoformat()} ({(due - today).days} days).", ""]
    out.append(f"### Overdue ({len(overdue)})")
    out += [f"- {a['due']} · {ref(a['id'])} · {a['title']} ({a.get('owner', DEFAULT_OWNER)})" for a in overdue] or ["- None"]
    out += ["", f"### Due in the next 14 days ({len(soon)})"]
    out += [f"- {a['due']} · {ref(a['id'])} · {a['title']} ({a.get('owner', DEFAULT_OWNER)})" for a in soon] or ["- None"]
    out += ["", "### External dates in the next 30 days"]
    out += [f"- {d['date']}{(' ' + d['time'] + ' ' + d.get('tz', agenda.get('timezone', ''))) if d.get('time') else ''} · {d['title']} ({d['confidence']})" for d in ext] or ["- None"]
    out += ["", "### Next gates"]
    for m in gates:
        out.append(f"- {m['date']} · {ref(m['id'])} · {m['title']}")
        out += [f"  - {c}" for c in m.get("criteria", [])]
    out += ["", f"### Decisions waiting ({len(decisions)})"]
    out += [f"- {ref(d['id'])} · {d['question']}{' (asked ' + str(d['asked_on']) + ')' if d['status'] == 'asked' else ''}" for d in decisions[:5]]
    if len(decisions) > 5:
        out.append(f"- ...and {len(decisions) - 5} more in data/decisions.yaml")
    out += ["", "_Generated by scripts/build.py from data/*.yaml._"]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- main

def git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip() or None
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--out", default="site", help="output directory (default: site)")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD) for the digest")
    ap.add_argument("--digest-only", action="store_true", help="write only digest.md")
    args = ap.parse_args(argv)

    bundle, index = load_all()
    errors, warnings = validate(bundle)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        print(f"{len(errors)} error(s); nothing written.", file=sys.stderr)
        return 1
    if args.check:
        print(f"ok: {sum(len(bundle[k]) for k in LIST_FILES)} items, {len(warnings)} warning(s)")
        return 0

    tz = ZoneInfo(bundle["agenda"].get("timezone", "America/New_York"))
    now_utc = dt.datetime.now(dt.timezone.utc)
    today = dt.date.fromisoformat(args.today) if args.today else now_utc.astimezone(tz).date()
    out = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    (out / "digest.md").write_text(build_digest(bundle, index, today), encoding="utf-8")
    if args.digest_only:
        print(f"wrote {out / 'digest.md'}")
        return 0

    payload = normalize(bundle)
    payload["index"] = index
    payload["meta"] = {
        "built_at": now_utc.replace(microsecond=0).isoformat(),
        "built_date": today.isoformat(),
        "commit": git_commit(),
        "repo": bundle["agenda"].get("repo", {}),
    }
    (out / "data.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "calendar.ics").write_text(build_ics(bundle, index, now_utc), encoding="utf-8", newline="")
    template = TEMPLATE.read_text(encoding="utf-8")
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    if "__AGENDA_DATA__" not in template:
        print("error: template is missing the __AGENDA_DATA__ placeholder", file=sys.stderr)
        return 1
    (out / "index.html").write_text(template.replace("__AGENDA_DATA__", blob), encoding="utf-8")
    print(f"wrote {out}/index.html, data.json, calendar.ics, digest.md ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
