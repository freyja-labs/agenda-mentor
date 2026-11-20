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
from urllib.parse import urlencode, urlparse

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
# The intake answers the draft prompt uses, in form order. Facultory stores the same six
# (INTAKE_KEYS in its lib/agenda.ts), and the schema's intake object must list them.
INTAKE_FIELDS = ["wants", "funding", "people", "load", "context", "constraints"]
PROFILE_REQUIRED = ["id", "name", "summary", "agenda_term", "agenda_title_prefix", "academy", "ladder",
                    "record_norms", "venues", "funders", "metric_conventions", "makeorbreak_archetypes",
                    "alignment_frameworks", "application_leaders", "convening_forms", "community_cycle",
                    "pitfalls", "verify_note"]

PAGES = ["method", "whiteboard", "prompts", "profiles", "mentors", "verify", "track", "about"]

# Response headers for the Cloudflare static assets the site is served from (_headers).
# The pages run no inline script or style and load nothing from another origin, so the
# policy can be strict; keep it that way. form-action 'none': the builder's form never
# submits, so the answers typed into it can never reach a URL or a server log.
HEADERS = """\
/*
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none'
  Strict-Transport-Security: max-age=31536000
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Cross-Origin-Opener-Policy: same-origin
/assets/fonts/*
  Cache-Control: public, max-age=2592000
"""

# Internal links are written as .../index.html in the templates; the build points them
# at the directory (.../), the form Cloudflare serves without a redirect.
INDEX_LINK = re.compile(r'href="((?![a-z]+:|#)[^"#]*?)index\.html(?=["#])')

# Facultory's app honors ?next= only for an in-app route like '#/agenda'; anything else
# is ignored there, so a malformed value here would send visitors to the dashboard.
FAC_NEXT = re.compile(r"#/[a-z0-9][a-z0-9/_-]{0,62}")


def facultory_links(fac: dict) -> dict:
    """The sign-up and sign-in links. They name this site as the source and nothing else."""
    signup = {"lane": "individual", "step": "plan", "plan": fac["plan"], "heard": fac["heard"], "next": fac["next"]}
    return {"url": fac["url"],
            "signup": f"{fac['url']}/signup?{urlencode(signup)}",
            "app": f"{fac['url']}/app?{urlencode({'next': fac['next']})}"}


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


def md_inline(text: str) -> str:
    """One paragraph of Markdown as HTML with no <p> around it, for a caption."""
    return re.sub(r"^<p>([\s\S]*)</p>$", r"\1", md(text.strip()).strip())


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

def check(cfg, profiles, prompts, anatomy, stages) -> list[str]:
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
    site_url = str(cfg.get("site_url", ""))
    if not re.fullmatch(r"https://[a-z0-9.-]+(?::\d+)?/(?:[A-Za-z0-9._~-]+/)*", site_url):
        errors.append("config.yaml: site_url must be an https address ending in '/', such as https://mentor.freyjalabs.com/")
    elif schema.get("$id") != f"{site_url}data/agenda.schema.json":
        errors.append(f"schema $id must be {site_url}data/agenda.schema.json, where the build publishes it")
    pub = cfg.get("publisher")
    if not (isinstance(pub, dict) and 0 < len(str(pub.get("name", "")).strip()) <= 60
            and re.fullmatch(r"https://[a-z0-9.-]+(?:/\S*)?", str(pub.get("url", "")))):
        errors.append("config.yaml: publisher needs a name (1 to 60 characters) and an https url")
    fac = cfg.get("facultory")
    if not isinstance(fac, dict):
        errors.append("config.yaml: the facultory block is missing")
    else:
        if not re.fullmatch(r"https://[a-z0-9.-]+(?::\d+)?", str(fac.get("url", ""))):
            errors.append("config.yaml: facultory.url must be an https origin with no path, such as https://facultory.com")
        if not FAC_NEXT.fullmatch(str(fac.get("next", ""))):
            errors.append("config.yaml: facultory.next must be an in-app route such as '#/agenda'")
        if not re.fullmatch(r"[a-z0-9-]{1,40}", str(fac.get("plan", ""))):
            errors.append("config.yaml: facultory.plan must be a plan slug such as 'noai'")
        if not 0 < len(str(fac.get("heard", "")).strip()) <= 60:
            errors.append("config.yaml: facultory.heard must be 1 to 60 characters")
    intake = schema["properties"].get("intake", {}).get("properties", {})
    if list(intake) != INTAKE_FIELDS:
        errors.append(f"schema intake keys {list(intake)} do not match the builder's intake fields {INTAKE_FIELDS}")
    errors += check_walkthrough(stages, {p["id"]: p["n"] for p in prompts})
    return errors


def check_walkthrough(stages, prompt_numbers) -> list[str]:
    """The home page walkthrough draws one scene per stage and captions it from the stage."""
    errors = []
    for s in stages:
        where = f"data/stages.yaml {s.get('id', '?')}"
        walk = str(s.get("walk", "")).strip()
        words = len(re.sub(r"\]\([^)]*\)", "]", walk).split())
        if not 0 < words <= 30:
            errors.append(f"{where}: walk has {words} words; the walkthrough caption needs 1 to 30")
        named = {int(n) for n in re.findall(r"\b[Pp]rompt (\d+)", walk)}
        own = prompt_numbers.get(s.get("prompt", ""))
        if named and named != {own}:
            errors.append(f"{where}: walk names prompt {sorted(named)}, but this stage uses prompt {own}")
    svg = (TEMPLATES / "partials" / "walkthrough.svg").read_text(encoding="utf-8")
    classes = " ".join(re.findall(r'class="([^"]*)"', svg)).split()
    scenes = {int(m.group(1)) for c in classes if (m := re.fullmatch(r"(?:on|a)(\d+)", c))}
    if scenes != set(range(1, len(stages) + 1)):
        errors.append(f"templates/partials/walkthrough.svg draws scenes {sorted(scenes)}; "
                      f"data/stages.yaml has {len(stages)} stages")
    return errors


def check_links(out: Path, base_path: str = "/") -> list[str]:
    errors = []
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        for href in re.findall(r'(?:href|src)="([^"#?]+)(?:[#?][^"]*)?"', text):
            if re.match(r"^(https?:|mailto:|data:)", href):
                continue
            # The 404 page links from the site root, because it is served at any depth.
            if href.startswith("/"):
                if not href.startswith(base_path):
                    errors.append(f"{page.relative_to(out)}: link '{href}' is outside the site's path {base_path}")
                    continue
                target = (out / href[len(base_path):]).resolve()
            else:
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

    errors = check(cfg, profiles, prompts, anatomy, stages)
    if errors:
        print("\n".join(f"error: {e}" for e in errors), file=sys.stderr)
        return 1

    repo_url = f"https://github.com/{cfg['repo']}"
    fac = facultory_links(cfg["facultory"])
    schema = json.loads((ROOT / "schema" / "agenda.schema.json").read_text(encoding="utf-8"))
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

    site_url = cfg["site_url"]
    base_path = urlparse(site_url).path
    canonicals: list[str] = []

    def write(rel: str, template: str, root: str | None = None, indexable: bool = True, **ctx):
        if root is None:
            root = "../" * rel.count("/")
        canonical = site_url + rel.removesuffix("index.html") if indexable else None
        page_html = env.get_template(template).render(
            cfg=cfg, nav=nav, root=root, repo_url=repo_url, fac=fac, current=ctx.get("slug", ""),
            canonical=canonical, **ctx)
        page_html = INDEX_LINK.sub(lambda m: f'href="{m.group(1) or "./"}', page_html)
        target = build_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page_html, encoding="utf-8")
        if canonical:
            canonicals.append(canonical)

    includes = {
        "stages": lambda root: env.get_template("partials/stages.html").render(stages=stages, prompts=prompt_by_id, root=root),
        "anatomy": lambda root: env.get_template("partials/anatomy.html").render(anatomy=anatomy),
        "rubric": lambda root: env.get_template("partials/rubric.html").render(rubric=rubric),
        "sessions": lambda root: env.get_template("partials/sessions.html").render(sessions=sessions),
        "checklist": lambda root: env.get_template("partials/checklist.html").render(checklist=checklist),
        "board": lambda root: env.get_template("partials/board.svg").render(redpen=True, label="whiteboard-layout"),
        "facultory": lambda root: env.get_template("partials/facultory.html").render(fac=fac),
    }

    def render_content(slug: str, root: str):
        meta, body = read_page(slug)
        body = (body.replace("{{repo_url}}", repo_url)
                .replace("{{facultory_signup}}", fac["signup"]).replace("{{facultory_app}}", fac["app"]))
        body_html = md(body)
        for key, fn in includes.items():
            body_html = re.sub(rf"<p>\[\[{key}\]\]</p>|\[\[{key}\]\]", lambda _m, f=fn: f(root), body_html)
        body_html, toc = add_heading_ids(body_html)
        return meta, body_html, toc

    # Home: a one-line promise and the walkthrough, one scene and one caption per stage.
    walk = [{**s, "walk_html": md_inline(str(s["walk"]).replace("{{facultory_signup}}", fac["signup"]))}
            for s in stages]
    write("index.html", "home.html", slug="", stages=walk)

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
        # For "Download your answers": the file Facultory's Import JSON reads.
        "format": schema["properties"]["format"]["const"],
        "intakeKeys": INTAKE_FIELDS,
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

    # Served at any depth for any address that matches no file, so it links from the root.
    write("404.html", "404.html", root=base_path, indexable=False, slug="")

    # Hosting files: Cloudflare's response headers, and what search engines read.
    (build_dir / "_headers").write_text(HEADERS, encoding="utf-8")
    (build_dir / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site_url}sitemap.xml\n", encoding="utf-8")
    (build_dir / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in sorted(canonicals))
        + "</urlset>\n", encoding="utf-8")

    link_errors = check_links(build_dir, base_path)
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
