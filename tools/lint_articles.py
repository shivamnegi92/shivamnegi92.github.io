"""Editorial linter for articles/*.md (stdlib only).

Checks the things a reviewer should never have to catch by hand:
structure, metadata, code that does not parse, diagram syntax traps,
unsourced numbers, broken internal links, and honest dating.

Usage: python3 tools/lint_articles.py        (exit 1 on any error)
"""
from __future__ import annotations

import ast
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_articles import SRC, parse  # noqa: E402

ROOT = SRC.parent
MIN_WORDS = 2_000
WEASEL = ("illustrative", "my experience")      # numbers must be sourced or derivable
HYPE = ("revolutionary", "game-changer", "game changer", "mind-blowing", "100x", "10x")
BANNED_CHARS = {"\u2014": "em dash"}

def prose_word_count(body: str) -> int:
    """Count prose only, excluding front matter, diagram DSL, and fenced code."""
    body = re.sub(r"^:::[^\n]*\n.*?^:::$", " ", body, flags=re.S | re.M)
    body = re.sub(r"^```.*?^```$", " ", body, flags=re.S | re.M)
    body = re.sub(r"^---.*?^---\s*", " ", body, flags=re.S | re.M)
    return len(re.findall(r"\b[\w’'-]+\b", body))


def lint(a: dict) -> list[str]:
    errs, body, slug = [], a["body"], a["slug"]

    # --- word count: actual prose, not diagram labels or code fences
    words = prose_word_count(body)
    if words < MIN_WORDS:
        errs.append(f"{words} prose words (minimum {MIN_WORDS}; code and diagram markup excluded)")

    # --- metadata
    if not 50 <= len(a["summary"]) <= 200:
        errs.append(f"summary length {len(a['summary'])} (want 50-200 for meta description)")
    if len(a["title"]) > 95:
        errs.append(f"title too long ({len(a['title'])} chars)")
    if date.fromisoformat(a["date"]) > date.today():
        errs.append("date is in the future")
    if len(a["tags"]) < 2:
        errs.append("needs at least 2 tags")

    # --- structure
    if a["kind"] == "guide" and "## Key takeaways" not in body:
        errs.append("guide missing '## Key takeaways'")
    if a["kind"] == "review":
        if "## Verdict" not in body:
            errs.append("review missing '## Verdict'")
        if not (ROOT / a["book"]["img"]).exists():
            errs.append("cover image missing")
        if not re.fullmatch(r"97[89]\d{10}", a["book"]["isbn"]):
            errs.append("ISBN-13 malformed")
        if not 1 <= float(a["rating"]) <= 5:
            errs.append("rating out of range")
    if "**Further reading:**" not in body and a["kind"] == "guide":
        errs.append("guide missing a 'Further reading' line with sources")

    # --- diagrams
    blocks = re.findall(r"^:::(\w+) ?([^\n]*)\n(.*?)^:::$", body, re.S | re.M)
    if len(blocks) < 4:
        errs.append(f"only {len(blocks)} diagrams (min 4)")
    for kind, caption, content in blocks:
        if not caption.strip():
            errs.append(f"{kind} diagram without caption")
        if any(w in caption.lower() for w in WEASEL):
            errs.append(f"unsourced numbers in diagram: '{caption.strip()}'")
        for line in content.splitlines():
            if re.search(r"[*!~]{2,}(\s|\||$)", line):
                errs.append(f"stacked style markers in diagram line: '{line.strip()}'")
        if kind == "flow":
            for line in content.splitlines():
                first = line.split("->")[0]
                if ":" in first and not re.match(r"^[a-z]+: ", line.strip()):
                    errs.append(f"flow node contains ':' and would be parsed as a row label: '{first.strip()}'")

    # --- code must parse
    for lang, code in re.findall(r"^```(\w*)\n(.*?)^```$", body, re.S | re.M):
        if lang == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                errs.append(f"python block does not parse: {e.msg} (line {e.lineno})")

    # --- internal links to sibling articles must exist
    for target in re.findall(r"\]\(\.\./([a-z0-9-]+)/\)", body):
        if not (SRC / f"{target}.md").exists() and not any(
                parse(p)["slug"] == target for p in SRC.glob("*.md")):
            errs.append(f"broken internal link ../{target}/")

    # --- prose hygiene
    low = body.lower() + a["title"].lower()
    for h in HYPE:
        if h in low:
            errs.append(f"hype word '{h}'")
    for ch, name in BANNED_CHARS.items():
        if ch in body:
            errs.append(f"contains {name}")
    return [f"{slug}: {e}" for e in errs]


def main() -> int:
    arts = [parse(p) for p in sorted(SRC.glob("*.md"))]
    errors = [e for a in arts for e in lint(a)]
    print("\n".join(errors) if errors else f"OK: {len(arts)} articles pass")
    print(f"{len(errors)} issue(s)", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
