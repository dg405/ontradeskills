"""Helpers for the on-trade Obsidian vault.

Resolves the vault root, reads/writes YAML frontmatter, and slugifies titles.
Pure-stdlib so the skills can shell out to it without extra deps.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

VAULT_ENV = "ONTRADE_VAULT"


def vault_root() -> Path:
    if VAULT_ENV in os.environ:
        return Path(os.environ[VAULT_ENV]).expanduser()
    return Path.cwd()


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\s-]", "", name.strip().lower())
    return re.sub(r"[-\s]+", "-", s).strip("-")


_FM_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Minimal YAML-ish parser for our flat frontmatter blocks.

    Supports: scalars, inline lists, nested one-level mappings, and multiline
    block lists. Good enough for our vault, not a general YAML parser.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    data: dict = {}
    current_key = None
    current_map_key = None
    for line in raw.splitlines():
        if not line.strip():
            current_map_key = None
            continue
        if line.startswith("  ") and current_map_key:
            k, _, v = line.strip().partition(":")
            data[current_map_key][k.strip()] = _coerce(v.strip())
            continue
        if line.startswith("- ") and current_key:
            data.setdefault(current_key, []).append(_coerce(line[2:].strip()))
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        current_map_key = None
        current_key = key
        if val == "":
            data[key] = []  # ambiguous: list or map; gets overridden if mapping follows
            current_map_key = key
            data[key] = {}
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [_coerce(x.strip()) for x in inner.split(",") if x.strip()]
        else:
            data[key] = _coerce(val)
    # tidy any empty mapping that got nothing under it -> [] is safer for our schema
    for k, v in list(data.items()):
        if v == {}:
            data[k] = []
    return data, body


def _coerce(v: str):
    if v == "" or v is None:
        return None
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v.strip('"').strip("'")


def dump_frontmatter(data: dict) -> str:
    lines = ["---"]
    for k, v in data.items():
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
        elif isinstance(v, dict):
            lines.append(f"{k}:")
            for ik, iv in v.items():
                lines.append(f"  {ik}: {'' if iv is None else iv}")
        else:
            lines.append(f"{k}: {'' if v is None else v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def read_note(path: Path) -> tuple[dict, str]:
    return parse_frontmatter(path.read_text(encoding="utf-8")) if path.exists() else ({}, "")


def write_note(path: Path, frontmatter: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_frontmatter(frontmatter) + body.lstrip("\n"), encoding="utf-8")


def find_venue(title: str, vault: Path | None = None) -> Path | None:
    vault = vault or vault_root()
    venues = vault / "Venues"
    if not venues.exists():
        return None
    target = slugify(title)
    for p in venues.glob("*.md"):
        if slugify(p.stem) == target:
            return p
    # fuzzy: any venue whose slug contains the target or vice versa
    for p in venues.glob("*.md"):
        s = slugify(p.stem)
        if target in s or s in target:
            return p
    return None


def cli():
    """Tiny CLI so skills can shell out from Bash without writing Python inline."""
    if len(sys.argv) < 2:
        print(json.dumps({"vault": str(vault_root())}))
        return
    cmd = sys.argv[1]
    if cmd == "vault":
        print(vault_root())
    elif cmd == "slug":
        print(slugify(sys.argv[2]))
    elif cmd == "find-venue":
        p = find_venue(sys.argv[2])
        print(p or "")
    else:
        sys.exit(f"unknown subcommand: {cmd}")


if __name__ == "__main__":
    cli()
