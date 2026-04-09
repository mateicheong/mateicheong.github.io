#!/usr/bin/env python3
"""Prefix home/away cells in friendlies-table with country flags (idempotent)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_CLUBS = ROOT / "content" / "clubs"

FLAG_IMG = '<img src="/images/flags/{flag}" width="18" alt="" class="friendlies-flag"> '

PLAIN_FLAG_RULES: list[tuple[str, str]] = [
    ("Nova Iguaçu", "br.svg"),
    ("Novo Hamburgo", "br.svg"),
    ("Calgary Foothills", "ca.svg"),
    ("Valour FC", "ca.svg"),
    ("Sigma FC", "ca.svg"),
    ("Cavalry FC", "ca.svg"),
    ("York United FC", "ca.svg"),
    ("York United", "ca.svg"),
    ("CF Montréal B", "ca.svg"),
    ("CF Montréal", "ca.svg"),
    ("Ottawa South United", "ca.svg"),
    ("CS Saint-Laurent", "ca.svg"),
    ("AS Laval", "ca.svg"),
    ("FC Laval", "ca.svg"),
    ("Halifax Wanderers FC", "ca.svg"),
    ("Vancouver Whitecaps FC", "ca.svg"),
    ("Toronto FC", "ca.svg"),
    ("Pacific FC", "ca.svg"),
    ("New York City FC", "us.svg"),
    ("Calgary Foothills", "ca.svg"),
    ("Mont-Royal Outremont", "ca.svg"),
    ("Atlético Ottawa", "ca.svg"),
]

SKIP_INNER = frozenset({"—", "–", "-", "&mdash;", "&#8212;", ""})


def flag_for_inner(inner: str) -> str | None:
    s = inner.strip()
    if not s or s in SKIP_INNER or "friendlies-flag" in s:
        return None
    if "/clubs/" in s:
        return "ca.svg"
    for name, fl in PLAIN_FLAG_RULES:
        if s.startswith(name) or (name in s and "<a " not in s):
            return fl
    if re.match(r"^[A-Za-z0-9]", s) and "<a " not in s:
        return "ca.svg"
    if "<a " in s:
        return "ca.svg"
    return "ca.svg"


def process_row(row_html: str) -> str:
    td_re = re.compile(r"<td([^>]*)>(.*?)</td>", re.DOTALL)
    matches = list(td_re.finditer(row_html))
    if len(matches) != 6:
        return row_html
    out: list[str] = []
    last = 0
    for i, m in enumerate(matches):
        out.append(row_html[last : m.start()])
        attrs, inner = m.group(1), m.group(2)
        if i in (2, 4):
            fl = flag_for_inner(inner)
            if fl:
                inner = FLAG_IMG.format(flag=fl) + inner
        out.append(f"<td{attrs}>{inner}</td>")
        last = m.end()
    out.append(row_html[last:])
    return "".join(out)


def process_tbody(tbody: str) -> str:
    parts: list[str] = []
    pos = 0
    for m in re.finditer(r"<tr[^>]*>.*?</tr>", tbody, re.DOTALL):
        parts.append(tbody[pos : m.start()])
        parts.append(process_row(m.group(0)))
        pos = m.end()
    parts.append(tbody[pos:])
    return "".join(parts)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    start = text.find("\n## Friendlies")
    if start == -1:
        return False
    end = text.find("\n## Competitions", start)
    if end == -1:
        prefix = text[:start]
        middle = text[start:]
        suffix = ""
    else:
        prefix = text[:start]
        middle = text[start:end]
        suffix = text[end:]

    table_re = re.compile(
        r'(<table class="[^"]*friendlies-table[^"]*"[^>]*>\s*<tbody>)(.*?)(</tbody>\s*</table>)',
        re.DOTALL,
    )

    def repl(m: re.Match[str]) -> str:
        return m.group(1) + process_tbody(m.group(2)) + m.group(3)

    new_middle, n = table_re.subn(repl, middle)
    new_text = prefix + new_middle + suffix
    if n and new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    updated = 0
    for path in sorted(CONTENT_CLUBS.rglob("*.md")):
        if process_file(path):
            print(path.relative_to(ROOT))
            updated += 1
    print(f"Updated {updated} files.", file=sys.stderr)


if __name__ == "__main__":
    main()
