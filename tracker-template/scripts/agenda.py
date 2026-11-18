#!/usr/bin/env python3
"""Small command-line helper for the tracker. Edits YAML in place, line by line,
so comments and ordering survive.

    python scripts/agenda.py status                  # what is overdue, due soon, and waiting
    python scripts/agenda.py set A-004 done          # set status on any item with that id
    python scripts/agenda.py set A-003 waiting --note "District reply expected Feb 10"
    python scripts/agenda.py decide D-03 "Collaborate on the shared dataset"
    python scripts/agenda.py add-action "Email the program officer" --due 2027-01-15 --thrust T1 --links F-02

After editing, run `python scripts/build.py --check`, then commit and push.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

DATA = build.DATA
ID_LINE = re.compile(r"^(\s*)-\s+id:\s*[\"']?([A-Za-z0-9_-]+)[\"']?\s*$")


def q(s: str) -> str:
    """YAML-safe double-quoted scalar."""
    return json.dumps(s, ensure_ascii=False)


def find(item_id: str):
    for path in sorted(DATA.glob("*.yaml")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            m = ID_LINE.match(line)
            if m and m.group(2) == item_id:
                indent = len(m.group(1)) + 2
                end = i + 1
                while end < len(lines):
                    nxt = lines[end]
                    if ID_LINE.match(nxt) or (nxt.strip() and len(nxt) - len(nxt.lstrip()) < indent):
                        break
                    end += 1
                while end > i + 1 and not lines[end - 1].strip():
                    end -= 1
                return path, lines, i, end, " " * indent
    raise SystemExit(f"no item with id {item_id}")


def set_field(lines, start, end, pad, key, value):
    pat = re.compile(rf"^{pad}{re.escape(key)}:")
    for j in range(start + 1, end):
        if pat.match(lines[j]):
            lines[j] = f"{pad}{key}: {value}"
            return end
    lines.insert(end, f"{pad}{key}: {value}")
    return end + 1


def cmd_set(args):
    path, lines, start, end, pad = find(args.id)
    end = set_field(lines, start, end, pad, "status", args.status)
    end = set_field(lines, start, end, pad, "updated", dt.date.today().isoformat())
    if args.note:
        set_field(lines, start, end, pad, "note", q(args.note))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{args.id}: status -> {args.status} ({path.name})")


def cmd_decide(args):
    path, lines, start, end, pad = find(args.id)
    end = set_field(lines, start, end, pad, "status", "decided")
    end = set_field(lines, start, end, pad, "answer", q(args.answer))
    set_field(lines, start, end, pad, "decided_on", dt.date.today().isoformat())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{args.id}: decided ({path.name})")


def cmd_add_action(args):
    path = DATA / "actions.yaml"
    text = path.read_text(encoding="utf-8")
    nums = [int(n) for n in re.findall(r"^- id: A-(\d+)", text, flags=re.M)]
    new_id = f"A-{(max(nums) + 1 if nums else 1):03d}"
    if not args.owner:
        bundle, _ = build.load_all()
        args.owner = bundle["agenda"].get("owner") or "Owner"
    block = [
        "", f"- id: {new_id}", f"  title: {q(args.title)}", f"  due: {args.due}",
        f"  thrust: [{', '.join(args.thrust)}]", f"  owner: {q(args.owner)}", "  status: open",
        f"  priority: {args.priority}", f"  done_when: {q(args.done_when or '')}",
        f"  links: [{', '.join(args.links or [])}]",
    ]
    path.write_text(text.rstrip("\n") + "\n" + "\n".join(block) + "\n", encoding="utf-8")
    print(f"added {new_id}")


def cmd_status(args):
    bundle, index = build.load_all()
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    print(build.build_digest(bundle, index, today))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--today"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("set"); s.add_argument("id"); s.add_argument("status"); s.add_argument("--note"); s.set_defaults(fn=cmd_set)
    s = sub.add_parser("decide"); s.add_argument("id"); s.add_argument("answer"); s.set_defaults(fn=cmd_decide)
    s = sub.add_parser("add-action"); s.add_argument("title"); s.add_argument("--due", required=True)
    s.add_argument("--thrust", nargs="+", default=["X"]); s.add_argument("--owner", default=None)
    s.add_argument("--priority", default="normal", choices=["high", "normal", "low"])
    s.add_argument("--done-when"); s.add_argument("--links", nargs="*"); s.set_defaults(fn=cmd_add_action)
    args = ap.parse_args(argv)
    args.fn(args)
    if args.cmd != "status":
        bundle, _ = build.load_all()
        errors, _ = build.validate(bundle)
        if errors:
            print("validation errors after edit:", *errors, sep="\n  ", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
