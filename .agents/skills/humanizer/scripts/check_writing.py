"""Check selected mechanical writing rules; never rewrite the input."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


CANNED = re.compile(
    r"\b(?:great question|let['’]s dive (?:in|into)|it['’]s worth noting|"
    r"bottom line|in conclusion|at the end of the day|let that sink in|"
    r"that['’]s where .{1,45}? comes in)\b", re.IGNORECASE)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2705\u274C\u2728]")


def prose_lines(content):
    """Yield line numbers and prose, leaving technical/quoted regions out."""
    fence = None
    frontmatter = False
    for number, raw in enumerate(content.splitlines(), 1):
        stripped = raw.strip()
        if number == 1 and stripped == "---":
            frontmatter = True
            yield number, ""
            continue
        if frontmatter:
            if stripped in ("---", "..."):
                frontmatter = False
            yield number, ""
            continue
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", raw)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            yield number, ""
            continue
        if marker:
            fence = marker[1]
            yield number, ""
            continue
        if stripped.startswith(">") or raw.startswith(("    ", "\t")) or re.match(r"^\s{0,3}\[[^]]+\]:\s*\S", raw):
            yield number, ""
            continue
        line = re.sub(r"(`+).*?\1", "", raw)
        line = re.sub(r"\[([^]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"https?://\S+", "", line)
        yield number, line


def check(content, mode="plain"):
    if mode not in ("plain", "document"):
        raise ValueError("Unknown writing mode")
    findings = []
    paragraph = []
    seen = set()

    def add(line, rule, detail):
        findings.append({"line": line, "rule": rule, "detail": detail})

    def finish():
        if paragraph:
            normalized = " ".join(part.strip() for _, part in paragraph)
            if len(normalized.split()) >= 8:
                if normalized in seen:
                    add(paragraph[0][0], "repeated-paragraph", "This paragraph repeats an earlier paragraph exactly")
                seen.add(normalized)
            paragraph.clear()

    for line_no, line in prose_lines(content):
        if not line.strip():
            finish()
            continue
        paragraph.append((line_no, line))
        for match in CANNED.finditer(line):
            add(line_no, "canned-phrase", match[0])
        if mode == "plain":
            if re.match(r"^\s{0,3}#{1,6}\s", line):
                add(line_no, "decorative-heading", "Use a paragraph unless a document heading is needed")
            if re.match(r"^\s{0,3}(?:[-*+]\s+|\d+[.)]\s+)?(?:(?:\*\*|__)[^*_]+:(?:\*\*|__)|(?:\*\*|__)[^*_]+(?:\*\*|__)(?:\s*[:—–-]|\s*$))", line):
                add(line_no, "bold-label", "Remove the label or express the point in the sentence")
            if re.fullmatch(r"\s*(?:[-*_]\s*){3,}", line):
                add(line_no, "horizontal-rule", "Remove decorative separation")
            if EMOJI.search(line):
                add(line_no, "decorative-emoji", "Use plain prose unless the requested voice needs emoji")
    finish()
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--mode", choices=("plain", "document"), default="plain")
    args = parser.parse_args()
    try:
        findings = check(args.path.read_text(encoding="utf-8-sig"), args.mode)
    except (OSError, UnicodeError) as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(json.dumps({"file": str(args.path), "mode": args.mode, "findings": findings}, ensure_ascii=True, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
