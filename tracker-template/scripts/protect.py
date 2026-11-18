#!/usr/bin/env python3
"""Encrypt the built dashboard so it can sit on a public GitHub Pages site.

The page that ships holds only ciphertext. The browser derives an AES-256-GCM key
from the password with PBKDF2-SHA256 and decrypts the dashboard locally, so the
password never leaves the browser. A short password defeats the scheme, because
anyone can copy the ciphertext and guess offline: use a long passphrase.

    DASHBOARD_PASSWORD='...' python scripts/protect.py --src site/index.html --out pages/index.html

The salt is fixed per site, so a key the browser remembers keeps working across
rebuilds; every build draws a fresh initialization vector.
"""
import argparse
import base64
import hashlib
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "site_src" / "protected.template.html"
ITERATIONS = 600_000
MIN_LENGTH = 12
SITE_LABEL = (os.environ.get("GITHUB_REPOSITORY", "agenda-tracker") + " dashboard v1").encode()
STORAGE_KEY = "agenda-tracker-dashboard-key:" + os.environ.get("GITHUB_REPOSITORY", "local")

# Added to the decrypted page: a Lock link that forgets a remembered key.
LOCK_SNIPPET = (
    "<script>(function(){var a=document.createElement('a');a.href='#';a.textContent='Lock';"
    "a.setAttribute('aria-label','Lock the dashboard');"
    "a.setAttribute('style','position:fixed;right:12px;bottom:12px;z-index:9999;font:13px system-ui,sans-serif;"
    "padding:6px 10px;background:Canvas;color:LinkText;border:1px solid GrayText;text-decoration:none');"
    "a.onclick=function(e){e.preventDefault();try{localStorage.removeItem('" + STORAGE_KEY + "')}catch(_){}"
    "location.reload()};(document.body||document.documentElement).appendChild(a);})();</script>"
)


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="site/index.html")
    ap.add_argument("--out", default="pages/index.html")
    ap.add_argument("--password-env", default="DASHBOARD_PASSWORD")
    args = ap.parse_args()

    password = os.environ.get(args.password_env, "")
    if len(password) < MIN_LENGTH:
        print(f"error: {args.password_env} is missing or shorter than {MIN_LENGTH} characters; "
              "nothing was published", file=sys.stderr)
        return 1

    html = Path(args.src).read_text(encoding="utf-8")
    if "</body>" in html:
        html = html.replace("</body>", LOCK_SNIPPET + "</body>", 1)
    else:
        html += LOCK_SNIPPET

    salt = hashlib.sha256(SITE_LABEL).digest()[:16]
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS, dklen=32)
    iv = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(iv, html.encode("utf-8"), None)  # ciphertext followed by the tag

    page = TEMPLATE.read_text(encoding="utf-8")
    for name, value in (("SALT", b64(salt)), ("IV", b64(iv)), ("DATA", b64(ciphertext)),
                        ("ITERATIONS", str(ITERATIONS)), ("STORAGE_KEY", STORAGE_KEY)):
        token = "{{" + name + "}}"
        if token not in page:
            print(f"error: template is missing {token}", file=sys.stderr)
            return 1
        page = page.replace(token, value)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} ({len(page):,} bytes, encrypted with AES-256-GCM, PBKDF2-SHA256 x {ITERATIONS:,})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
