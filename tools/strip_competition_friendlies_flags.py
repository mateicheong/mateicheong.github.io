#!/usr/bin/env python3
"""Remove friendlies-flag images from markdown after ## Competitions (competition result tables only)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_CLUBS = ROOT / "content" / "clubs"

IMG_RE = re.compile(
    r'<img src="/images/flags/[^"]+" width="18" alt="" class="friendlies-flag">\s*'
)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    marker = "\n## Competitions"
    idx = text.find(marker)
    if idx == -1:
        return False
    before = text[: idx + len(marker)]
    after = text[idx + len(marker) :]
    after_new = IMG_RE.sub("", after)
    if after_new == after:
        return False
    path.write_text(before + after_new, encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for path in sorted(CONTENT_CLUBS.rglob("*.md")):
        if process_file(path):
            print(path.relative_to(ROOT))
            n += 1
    print(f"Stripped competition flags from {n} files.", file=sys.stderr)


if __name__ == "__main__":
    main()
