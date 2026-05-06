"""Tiered menu fetcher.

Reliability ladder, in order:

  1. http        - plain GET, parse text from HTML.
  2. pdf         - if content-type or URL says PDF, run `pdftotext`.
  3. browser     - JS-rendered: Claude/skill should call mcp__Claude_in_Chrome.
                   We don't do this from Python; the skill orchestrates it.
                   This module exposes `needs_browser(text)` so the skill
                   knows when to escalate.
  4. vision      - last resort: skill takes a screenshot and passes to
                   the model. Again, orchestration lives in the skill.

Usage from a skill:

    python3 _lib/fetch.py http <url>             # tier 1
    python3 _lib/fetch.py pdf <local-path>       # tier 2 (after download)
    python3 _lib/fetch.py download <url> <dest>  # save remote file locally

Each tier prints to stdout: a JSON header line, then a blank line, then the
extracted text body. Empty body or `usable: false` means escalate.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 ontrade-skills/0.1"
TIMEOUT = 20

# A snippet is "usable" for menu analysis if it contains some signal of cocktails.
_DRINK_HINTS = re.compile(
    r"\b(cocktail|negroni|martini|spritz|highball|sour|gin|vodka|whisky|whiskey|"
    r"rum|tequila|mezcal|liqueur|bitters|vermouth|aperitif|amaro|signature|menu)\b",
    re.IGNORECASE,
)


class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        d = data.strip()
        if d:
            self.parts.append(d)


def _strip_html(html: str) -> str:
    s = _Stripper()
    try:
        s.feed(html)
    except Exception:
        pass
    return "\n".join(s.parts)


def needs_browser(text: str) -> bool:
    """Return True if the extracted body is too thin / non-menu-shaped."""
    t = (text or "").strip()
    if len(t) < 400:
        return True
    return not _DRINK_HINTS.search(t)


def _emit(header: dict, body: str = "") -> None:
    sys.stdout.write(json.dumps(header) + "\n\n")
    sys.stdout.write(body)
    sys.stdout.flush()


def tier_http(url: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            ct = resp.headers.get("Content-Type", "").lower()
            raw = resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        _emit({"tier": "http", "ok": False, "error": str(e), "usable": False})
        return 1

    if "application/pdf" in ct or url.lower().endswith(".pdf"):
        # caller should have used `download` then `pdf`; flag escalation.
        _emit({"tier": "http", "ok": True, "content_type": ct, "usable": False, "escalate": "pdf"})
        return 0

    text = _strip_html(raw.decode("utf-8", errors="replace"))
    usable = not needs_browser(text)
    _emit(
        {"tier": "http", "ok": True, "content_type": ct, "bytes": len(raw), "usable": usable},
        text,
    )
    return 0


def tier_pdf(path: str) -> int:
    p = Path(path).expanduser()
    if not p.exists():
        _emit({"tier": "pdf", "ok": False, "error": f"missing: {p}", "usable": False})
        return 1
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", str(p), "-"],
            check=True, capture_output=True, text=True, timeout=60,
        )
    except FileNotFoundError:
        _emit({"tier": "pdf", "ok": False, "error": "pdftotext not installed (brew install poppler)", "usable": False})
        return 1
    except subprocess.CalledProcessError as e:
        _emit({"tier": "pdf", "ok": False, "error": e.stderr.strip(), "usable": False})
        return 1
    text = out.stdout
    usable = not needs_browser(text)
    _emit({"tier": "pdf", "ok": True, "bytes": len(text), "usable": usable}, text)
    return 0


def tier_download(url: str, dest: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "")
    except Exception as e:
        _emit({"tier": "download", "ok": False, "error": str(e)})
        return 1
    p = Path(dest).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    _emit({"tier": "download", "ok": True, "path": str(p), "content_type": ct, "bytes": len(data)})
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: fetch.py {http|pdf|download} ...")
    cmd = sys.argv[1]
    if cmd == "http":
        return tier_http(sys.argv[2])
    if cmd == "pdf":
        return tier_pdf(sys.argv[2])
    if cmd == "download":
        return tier_download(sys.argv[2], sys.argv[3])
    sys.exit(f"unknown subcommand: {cmd}")


if __name__ == "__main__":
    sys.exit(main())
