#!/usr/bin/env python3
"""Regenerate _data/publications.json from the VUSec Zotero BibTeX export.

Run this whenever a new paper is out, check the result with
`bundle exec jekyll serve`, then commit and push:

    python3 scripts/update_publications.py

Optionally pass a different BibTeX URL or a local .bib file as the first
argument. Only the Python standard library is needed.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

BIB_URL = ("https://download.vusec.net/papers/zotero.php"
           "?q=Wiebing&full=&format=bibtex&sort=date")
OWNER = "Wiebing"          # author last name to highlight
KEYWORD = "type_paper"     # only keep entries with this keyword

OUT = Path(__file__).resolve().parent.parent / "_data" / "publications.json"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Artifact evaluation keyword -> (badge image, tooltip)
BADGES = {
    "artifacts:available": ("available.png", "Artifacts Available"),
    "artifacts:functional": ("evaluated.png", "Artifacts Functional"),
    "artifacts:reproduced": ("results.png", "Results Reproduced"),
}


def read_bib(source):
    if re.match(r"https?://", source):
        with urllib.request.urlopen(source, timeout=30) as resp:
            return resp.read().decode("utf-8")
    return Path(source).read_text(encoding="utf-8")


def parse_value(text, i):
    """Parse a field value starting at text[i]; return (value, next index)."""
    if text[i] == "{":
        depth, start = 0, i
        while True:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[start + 1:i], i + 1
            i += 1
    if text[i] == '"':
        end = text.index('"', i + 1)
        return text[i + 1:end], end + 1
    m = re.compile(r"[^,}\s]+").match(text, i)
    return m.group(0), m.end()


def parse_bibtex(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        entry = {"type": m.group(1).lower(), "key": m.group(2)}
        i = m.end()
        field = re.compile(r"\s*(\w+)\s*=\s*")
        while True:
            fm = field.match(text, i)
            if not fm:
                break
            value, i = parse_value(text, fm.end())
            entry[fm.group(1).lower()] = value
            i = re.compile(r"\s*,?").match(text, i).end()
        entries.append(entry)
    return entries


def clean(s):
    """Strip BibTeX braces/escapes and collapse whitespace."""
    s = re.sub(r"\\([&%$#_])", r"\1", s)
    s = s.replace("{", "").replace("}", "").replace("~", " ")
    return re.sub(r"\s+", " ", s).strip()


def short_name(name):
    """'de Faveri Tron, Alvise' -> 'de Faveri Tron, A.'"""
    if "," in name:
        last, first = [p.strip() for p in name.split(",", 1)]
    else:
        parts = name.split()
        last, first = parts[-1], " ".join(parts[:-1])
    initials = " ".join(p[0] + "." for p in re.split(r"[\s-]+", first) if p)
    return f"{last}, {initials}" if initials else last


def parse_links(url_field):
    """'Paper=https://a Web=https://b' -> [{label, url}, ...]"""
    return [{"label": label, "url": url}
            for label, url in re.findall(r"(\S+?)=(https?://\S+)", url_field)]


def month_name(value):
    value = value.strip().lower()
    if value.isdigit() and 1 <= int(value) <= 12:
        return MONTHS[int(value) - 1]
    for name in MONTHS:
        if name.lower().startswith(value[:3]):
            return name
    return ""


def to_publication(e):
    keywords = [k.strip() for k in clean(e.get("keywords", "")).split(",")]
    month = month_name(e.get("month", ""))
    venue = e.get("booktitle") or e.get("journal") or ""
    authors = [clean(a) for a in re.split(r"\s+and\s+", e.get("author", ""))]
    return {
        "title": clean(e.get("title", "")),
        "authors": [{"name": short_name(a),
                     "me": a.split(",")[0].strip() == OWNER}
                    for a in authors if a],
        "venue": clean(venue),
        "date": " ".join(p for p in [month, clean(e.get("year", ""))] if p),
        "year": clean(e.get("year", "")),
        "month": MONTHS.index(month) + 1 if month else 0,
        "note": clean(e.get("note", "")),
        "links": parse_links(e.get("url", "")),
        "badges": [{"image": BADGES[k][0], "title": BADGES[k][1]}
                   for k in keywords if k in BADGES],
        "_keywords": keywords,
    }


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else BIB_URL
    pubs = [to_publication(e) for e in parse_bibtex(read_bib(source))]
    pubs = [p for p in pubs if KEYWORD in p.pop("_keywords")]
    pubs.sort(key=lambda p: (p["year"], p["month"]), reverse=True)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(pubs, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"Wrote {len(pubs)} publications to _data/{OUT.name}")
    for p in pubs:
        print(f"  {p['year']}  {p['title']}")


if __name__ == "__main__":
    main()
