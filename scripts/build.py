#!/usr/bin/env python3
"""Build the Agenda Mentor site from content/, data/, prompts/, and templates/.

Usage:
    python scripts/build.py                # validate, then build into _site/
    python scripts/build.py --check        # validate only (the pull-request gate)
    python scripts/build.py --out public   # build somewhere else

Every link the build writes is relative, so the output works on a GitHub Pages project
path, a custom domain, any static host, or opened from disk.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
CONTENT, DATA, PROMPTS, TEMPLATES, ASSETS = (ROOT / d for d in ("content", "data", "prompts", "templates", "assets"))

# Fields the prompt builder can fill. A placeholder outside this set is a build error.
KNOWN_FIELDS = {
    "name", "surname", "title", "department", "institution", "field", "career_stage", "mentor",
    "wants", "funding", "people", "load", "context", "constraints", "whiteboard", "series",
    "date", "month_year", "year_plus_2", "year_plus_5", "year_plus_6", "makeorbreak_months",
    "horizon_years", "agenda_term", "agenda_title_prefix", "discipline_profile",
}
PROFILE_REQUIRED = ["id", "name", "summary", "agenda_term", "agenda_title_prefix", "academy", "ladder",
                    "record_norms", "venues", "funders", "metric_conventions", "makeorbreak_archetypes",
                    "alignment_frameworks", "application_leaders", "convening_forms", "community_cycle",
                    "pitfalls", "verify_note"]

PAGES = ["method", "whiteboard", "prompts", "profiles", "mentors", "verify", "track", "about"]


def load_yaml(name: str):
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def read_page(slug: str) -> tuple[dict, str]:
    text = (CONTENT / f"{slug}.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"content/{slug}.md: missing front matter")
    return yaml.safe_load(m.group(1)), m.group(2)


def read_prompts() -> list[dict]:
    """Prompt files: '# Prompt N: Title', usage notes, a '---' line, then the template."""
    out = []
    for path in sorted(PROMPTS.glob("0[1-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        head, sep, body = text.partition("\n---\n")
        if not sep:
            raise SystemExit(f"{path.name}: needs a '---' line between the notes and the prompt")
        m = re.match(r"# Prompt (\d+): (.+)\n", head)
        if not m:
            raise SystemExit(f"{path.name}: first line must be '# Prompt N: Title'")
        notes = head[m.end():].strip()
        out.append({"id": path.stem, "n": int(m.group(1)), "title": m.group(2).strip(),
                    "notes": notes, "body": body.strip() + "\n", "file": f"prompts/{path.name}"})
    return out


def md(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list", "sane_lists"])


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def add_heading_ids(body_html: str) -> tuple[str, list[dict]]:
    toc, used = [], set()

    def repl(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "id=" in attrs:
            return m.group(0)
        base = slugify(re.sub(r"<[^>]+>", "", inner)) or "section"
        hid, n = base, 2
        while hid in used:
            hid, n = f"{base}-{n}", n + 1
        used.add(hid)
        if level == "2":
            toc.append({"id": hid, "text": html.unescape(re.sub(r"<[^>]+>", "", inner))})
        return f'<h{level} id="{hid}"{attrs}>{inner}</h{level}>'

    return re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body_html), toc


def profile_block(p: dict) -> str:
    """The discipline profile as the Markdown block pasted into prompts 2, 3, and 6."""
    lines = [f"**{p['name']}**", "",
             f"- Highest recognition: {p['academy']['name']}. {p['academy']['basis'].strip()}"]
    for stage, label in (("early", "Early career"), ("mid", "Mid career"), ("senior", "Senior")):
        lines.append(f"- Recognition ladder, {label.lower()}: " + "; ".join(p["ladder"][stage]) + ".")
    lines += [f"- What counts as the record: {p['record_norms'].strip()}",
              f"- Flagship venues: {p['venues'].strip()}"]
    for key, label in (("funders", "Funders"), ("metric_conventions", "Metric conventions"),
                       ("makeorbreak_archetypes", "Make-or-break archetypes"),
                       ("alignment_frameworks", "Alignment frameworks"),
                       ("application_leaders", "Application leaders"), ("convening_forms", "Convening forms"),
                       ("community_cycle", "Community cycle, in order"), ("pitfalls", "Pitfalls to avoid")):
        lines.append(f"- {label}: " + "; ".join(p[key]) + ".")
    lines.append(f"- Verify: {p['verify_note'].strip()}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- checks

def check(cfg, profiles, prompts, anatomy) -> list[str]:
    errors = []
    ids = set()
    for p in profiles:
        for f in PROFILE_REQUIRED:
            if p.get(f) in (None, "", [], {}):
                errors.append(f"data/disciplines.yaml {p.get('id', '?')}: missing '{f}'")
        if p.get("id") in ids:
            errors.append(f"data/disciplines.yaml: duplicate id {p['id']}")
        ids.add(p.get("id"))
        for stage in ("early", "mid", "senior"):
            if not (p.get("ladder") or {}).get(stage):
                errors.append(f"data/disciplines.yaml {p.get('id')}: ladder.{stage} is empty")
    for pr in prompts:
        opens = len(re.findall(r"\{\{#if \w+\}\}", pr["body"]))
        closes = pr["body"].count("{{/if}}")
        if opens != closes:
            errors.append(f"{pr['file']}: {opens} '{{{{#if}}}}' blocks but {closes} '{{{{/if}}}}'")
        for var in set(re.findall(r"\{\{#?(?:if )?([a-z_0-9]+)\}\}", pr["body"])):
            if var not in KNOWN_FIELDS:
                errors.append(f"{pr['file']}: unknown placeholder '{{{{{var}}}}}'")
    nums = [pr["n"] for pr in prompts]
    if nums != list(range(1, len(nums) + 1)):
        errors.append(f"prompts/: numbering is {nums}; expected 1..{len(nums)} in file order")
    schema = json.loads((ROOT / "schema" / "agenda.schema.json").read_text(encoding="utf-8"))
    schema_keys = list(schema["properties"]["sections"]["properties"].keys())
    anatomy_keys = [a["key"] for a in anatomy]
    if schema_keys != anatomy_keys:
        errors.append(f"schema sections {schema_keys} do not match data/anatomy.yaml keys {anatomy_keys}")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", str(cfg.get("repo", ""))):
        errors.append("config.yaml: repo must be 'owner/name'")
    return errors


def check_links(out: Path) -> list[str]:
    errors = []
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        for href in re.findall(r'(?:href|src)="([^"#?]+)(?:[#?][^"]*)?"', text):
            if re.match(r"^(https?:|mailto:|data:)", href):
                continue
            target = (page.parent / href).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{page.relative_to(out)}: broken link '{href}'")
        if re.search(r"\{\{\s*[a-z_]+\s*\}\}", re.sub(r"<script[\s\S]*?</script>", "", text)):
            errors.append(f"{page.relative_to(out)}: unrendered placeholder in page text")
        if re.search(r"\[\[[a-z]+\]\]", text):
            errors.append(f"{page.relative_to(out)}: unreplaced [[include]]")
    return errors


# --------------------------------------------------------------------------- build

def build(out: Path, check_only: bool) -> int:
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    profiles = load_yaml("disciplines.yaml")
    stages, anatomy = load_yaml("stages.yaml"), load_yaml("anatomy.yaml")
    rubric, sessions, checklist = load_yaml("rubric.yaml"), load_yaml("sessions.yaml"), load_yaml("checklist.yaml")
    prompts = read_prompts()

    errors = check(cfg, profiles, prompts, anatomy)
    if errors:
        print("\n".join(f"error: {e}" for e in errors), file=sys.stderr)
        return 1

    repo_url = f"https://github.com/{cfg['repo']}"
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    env.filters["md"] = md
    nav = [{"slug": s, **read_page(s)[0]} for s in PAGES]
    nav.sort(key=lambda n: n.get("order", 99))
    prompt_by_id = {p["id"]: p for p in prompts}

    build_dir = out if not check_only else ROOT / ".check_site"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)
    shutil.copytree(ASSETS, build_dir / "assets")

    def write(rel: str, template: str, **ctx):
        depth = rel.count("/")
        root = "../" * depth
        page_html = env.get_template(template).render(
            cfg=cfg, nav=nav, root=root, repo_url=repo_url, current=ctx.get("slug", ""), **ctx)
        target = build_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page_html, encoding="utf-8")

    includes = {
        "stages": lambda root: env.get_template("partials/stages.html").render(stages=stages, prompts=prompt_by_id, root=root),
        "anatomy": lambda root: env.get_template("partials/anatomy.html").render(anatomy=anatomy),
        "rubric": lambda root: env.get_template("partials/rubric.html").render(rubric=rubric),
        "sessions": lambda root: env.get_template("partials/sessions.html").render(sessions=sessions),
        "checklist": lambda root: env.get_template("partials/checklist.html").render(checklist=checklist),
        "board": lambda root: env.get_template("partials/board.svg").render(redpen=True, label="whiteboard-layout"),
    }

    def render_content(slug: str, root: str):
        meta, body = read_page(slug)
        body = body.replace("{{repo_url}}", repo_url)
        body_html = md(body)
        for key, fn in includes.items():
            body_html = re.sub(rf"<p>\[\[{key}\]\]</p>|\[\[{key}\]\]", lambda _m, f=fn: f(root), body_html)
        body_html, toc = add_heading_ids(body_html)
        return meta, body_html, toc

    # Home
    write("index.html", "home.html", slug="", stages=stages, prompts=prompt_by_id, profiles=profiles,
          board=env.get_template("partials/board.svg").render(redpen=True, label="hero-board"))

    # Content pages
    for slug in ("method", "whiteboard", "mentors", "verify", "track", "about"):
        meta, body_html, toc = render_content(slug, "../")
        write(f"{slug}/index.html", "page.html", slug=slug, meta=meta, body=body_html, toc=toc)

    # Prompt builder
    meta, intro_html, _ = render_content("prompts", "../")
    portal = {
        "profiles": [{**p, "block": profile_block(p)} for p in profiles],
        "prompts": [{k: p[k] for k in ("id", "n", "title", "body", "file")} | {"notes_html": md(p["notes"])} for p in prompts],
        "known": sorted(KNOWN_FIELDS),
        "storageKey": "agenda-mentor:v1",
    }
    write("prompts/index.html", "prompts.html", slug="prompts", meta=meta, intro=intro_html, prompts=prompts,
          profiles=profiles, portal_json=json.dumps(portal, ensure_ascii=False).replace("</", "<\\/"))
    recon = (PROMPTS / "00-reconstructed.md").read_text(encoding="utf-8")
    recon_notes, _, recon_body = recon.partition("\n---\n")
    write("prompts/reconstruction/index.html", "reconstruction.html", slug="prompts",
          notes=md(re.sub(r"^# .+\n", "", recon_notes)), body=md(recon_body))

    # Profiles
    meta, intro_html, _ = render_content("profiles", "../")
    write("profiles/index.html", "profiles.html", slug="profiles", meta=meta, intro=intro_html, profiles=profiles)
    for p in profiles:
        write(f"profiles/{p['id']}/index.html", "profile.html", slug="profiles", p=p, block=profile_block(p))

    # Machine-readable copies for other tools (Facultory imports these).
    (build_dir / "data").mkdir()
    (build_dir / "data" / "disciplines.json").write_text(
        json.dumps([{**p, "block": profile_block(p)} for p in profiles], ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(ROOT / "schema" / "agenda.schema.json", build_dir / "data" / "agenda.schema.json")
    (build_dir / ".nojekyll").write_text("", encoding="utf-8")

    link_errors = check_links(build_dir)
    if check_only:
        shutil.rmtree(build_dir)
    if link_errors:
        print("\n".join(f"error: {e}" for e in link_errors), file=sys.stderr)
        return 1
    pages = len(list(out.rglob("*.html"))) if not check_only else 0
    print("check passed" if check_only else f"built {pages} pages into {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="validate data, prompts, and links without keeping output")
    ap.add_argument("--out", default="_site", help="output directory (default: _site)")
    args = ap.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    return build(out, args.check)


if __name__ == "__main__":
    sys.exit(main())
