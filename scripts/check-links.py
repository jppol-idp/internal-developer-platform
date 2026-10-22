#!/usr/bin/env python3
"""Find dead internal links and anchors in a built Jekyll site."""

import argparse
import os
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


DEFAULT_DOMAINS = ["docs.idp.jppol.dk", "public.docs.idp.jppol.dk"]
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("id", "name"):
            if attrs.get(key):
                self.ids.add(attrs[key])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "img" and attrs.get("src"):
            self.links.append(attrs["src"])


def resolve(site: Path, path: str) -> Path | None:
    """Resolve a URL path to a file the way GitHub Pages does."""
    target = site / unquote(path).lstrip("/")
    candidates = [target / "index.html"] if path.endswith("/") else [
        target, target.with_name(target.name + ".html"), target / "index.html"
    ]
    return next((c for c in candidates if c.is_file()), None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", nargs="?", default="_site", help="built site directory (default: _site)")
    parser.add_argument("--domain", action="append", help="host treated as this site; repeatable (default: %(default)s)")
    args = parser.parse_args()

    site = Path(args.site).resolve()
    domains = set(args.domain or DEFAULT_DOMAINS)

    pages = {}
    for file in site.rglob("*.html"):
        page = PageParser()
        page.feed(file.read_text(errors="replace"))
        pages[file] = page

    results = {}
    for file, page in sorted(pages.items()):
        # READMEs are written for GitHub, where relative .md links resolve
        if file.name == "README.html":
            continue
        page_url = "/" + file.relative_to(site).as_posix()
        errors = []
        for link in dict.fromkeys(page.links):
            url = urlsplit(urljoin(page_url, link.strip()))
            if url.scheme in SKIP_SCHEMES or (url.netloc and url.netloc not in domains):
                continue

            target = resolve(site, url.path or page_url)
            if target is None:
                errors.append((link, "page not found"))
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append((link, "anchor not found"))

        if errors:
            results[file.relative_to(site).as_posix()] = errors

    broken = sum(len(errors) for errors in results.values())
    total = f"{broken} broken link(s) across {len(pages)} pages"

    for page, errors in results.items():
        print(f"{page}:")
        for link, reason in errors:
            print(f"  {link} ({reason})")
    print(total)

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        lines = ["## Link check", "", f"{'❌' if broken else '✅'} {total}", ""]
        if results:
            lines += ["| Page | Link | Problem |", "|---|---|---|"]
            for page, errors in results.items():
                for link, reason in errors:
                    lines.append(f"| `{page}` | `{link.replace('|', '%7C')}` | {reason} |")
        with open(summary_file, "a") as summary:
            summary.write("\n".join(lines) + "\n")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
