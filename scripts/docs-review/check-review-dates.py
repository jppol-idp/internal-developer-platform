#!/usr/bin/env python3
"""Find overdue docs pages and write a JSON batch to stdout."""

import argparse
import json
import re
import sys
from calendar import monthrange
from datetime import date
from pathlib import Path


DOCS_BASE_URL = "https://docs.idp.jppol.dk"
DEFAULT_DIRS = ["how-to", "documentation", "onboarding"]


def parse_frontmatter(content: str) -> dict:
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^([\w]+):\s*(.+)$", line)
        if m:
            result[m.group(1)] = m.group(2).strip().strip("\"'")
    return result


def parse_date(date_str: str) -> "date | None":
    parts = date_str.strip().split("-")
    if len(parts) != 3:
        return None
    try:
        y, a, b = int(parts[0]), int(parts[1]), int(parts[2])
        if a > 12:
            # Non-standard YYYY-DD-MM (e.g. 2025-17-06 meaning June 17)
            a, b = b, a
        return date(y, a, b)
    except (ValueError, TypeError):
        return None


def add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, monthrange(year, month)[1])
    return date(year, month, day)


def parse_review_in(review_in: str) -> "int | None":
    m = re.match(r"(\d+)\s+months?", review_in.strip(), re.IGNORECASE)
    return int(m.group(1)) if m else None


def doc_url(file_path: Path, repo_root: Path, permalink: "str | None") -> str:
    if permalink:
        return f"{DOCS_BASE_URL}/{permalink.lstrip('/')}"
    rel = file_path.relative_to(repo_root)
    return f"{DOCS_BASE_URL}/{str(rel).removesuffix('.md')}.html"


def find_overdue(repo_root: Path, today: date, dirs: list, include_index: bool) -> list:
    overdue = []
    for search_dir in dirs:
        if not search_dir.is_dir():
            sys.exit(f"Error: directory '{search_dir}' does not exist")
        for md_file in sorted(search_dir.rglob("*.md")):
            if not include_index and md_file.name == "index.md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = parse_frontmatter(content)
            raw_date = fm.get("last_reviewed_on")
            raw_period = fm.get("review_in")
            if not raw_date or not raw_period:
                continue
            reviewed = parse_date(raw_date)
            if not reviewed:
                print(f"Warning: unparseable date '{raw_date}' in {md_file}", file=sys.stderr)
                continue
            months = parse_review_in(raw_period)
            if not months:
                continue
            expiry = add_months(reviewed, months)
            if expiry >= today:
                continue
            overdue.append({
                "title": fm.get("title", md_file.stem),
                "file": str(md_file.relative_to(repo_root)),
                "last_reviewed_on": reviewed.isoformat(),
                "expiry": expiry.isoformat(),
                "days_overdue": (today - expiry).days,
                "url": doc_url(md_file, repo_root, fm.get("permalink")),
            })
    overdue.sort(key=lambda x: x["days_overdue"], reverse=True)
    return overdue


def main():
    parser = argparse.ArgumentParser(
        description="Find overdue docs pages and write a JSON batch to a file."
    )
    parser.add_argument("--repo-root", default=".", help="Root of the docs repo")
    parser.add_argument("--limit", type=int, default=5, metavar="N")
    parser.add_argument("-d", "--dir", action="append", dest="dirs", metavar="DIR",
                        help=f"Restrict to files under this folder (repeatable, default: {DEFAULT_DIRS})")
    parser.add_argument("--include-index", action="store_true",
                        help="Include index.md files (excluded by default)")
    parser.add_argument("--output", default="overdue.json", metavar="FILE",
                        help="Path to write the JSON batch (default: overdue.json)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    today = date.today()
    dirs = [repo_root / d for d in (args.dirs or DEFAULT_DIRS)]

    overdue = find_overdue(repo_root, today, dirs=dirs, include_index=args.include_index)
    batch = overdue[: args.limit]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"date": today.isoformat(), "total_overdue": len(overdue), "batch": batch}, f, indent=2)

    batch_titles = {doc["title"] for doc in batch}
    lines = [
        "## Docs review reminder",
        f"**Total overdue:** {len(overdue)} | **Selected:** {len(batch)}",
        "",
        "| Page | Days overdue | Selected |",
        "|------|-------------|----------|",
    ]
    for doc in overdue:
        selected = "x" if doc["title"] in batch_titles else ""
        lines.append(f"| [{doc['title']}]({doc['url']}) | {doc['days_overdue']} | {selected} |")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
