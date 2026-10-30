"""The landing page's "What's new": the latest releases of the product repositories and the date each
documentation site was last updated, read from the GitHub API when the site is built.

The page carries two kinds of marker:

    <!-- releases -->            the latest releases across the product repositories, newest first
    <!-- updated: PAROL-docs --> the date of the last commit on main of that documentation repository

Without network, or when the API's rate limit is reached, the markers render as nothing and the page is still
complete. The CI passes GITHUB_TOKEN for a higher rate limit and rebuilds the page every week (pages.yml), so the
list stays fresh without a push.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime

ORG = "Source-Robotics"
PRODUCTS = [  # product name, repository with the releases, what a release is called
    ("PAROL6", "PAROL6-Desktop-robot-arm", "release"),
    ("MSG gripper", "MSG-compliant-AI-stepper-gripper", "release"),
    ("SSG-48 gripper", "SSG-48-adaptive-electric-gripper", "release"),
    ("STEPFOC", "STEPFOC-stepper-controller", "firmware"),
    ("Spectral Micro", "Spectral-Micro-BLDC-controller", "firmware"),
]
MAX_RELEASES = 8
RELEASES_RE = re.compile(r"<!--\s*releases\s*-->")
UPDATED_RE = re.compile(r"<!--\s*updated:\s*([\w.-]+)\s*-->")
_cache: dict[str, object] = {}


def api(path: str):
    if path in _cache:
        return _cache[path]
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": "application/vnd.github+json",
                                                                             "User-Agent": "source-robotics-docs"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
    except Exception:          # offline, rate limited, repository gone: the marker renders empty
        data = None
    _cache[path] = data
    return data


def day(iso: str) -> str:
    return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%-d %B %Y") if os.name != "nt" else \
        datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%#d %B %Y")


def releases() -> str:
    items = []
    for product, repo, kind in PRODUCTS:
        for rel in (api(f"repos/{ORG}/{repo}/releases?per_page=3") or [])[:3]:
            if rel.get("draft") or not rel.get("published_at"):
                continue
            tag = rel.get("tag_name") or ""
            items.append((rel["published_at"], f"- **{product}** {kind} {tag.lstrip('Vv')}: "
                                               f"[{rel.get('name') or tag}]({rel['html_url']}), {day(rel['published_at'])}"))
    items.sort(reverse=True)
    return "\n".join(line for _, line in items[:MAX_RELEASES])


def updated(repo: str) -> str:
    commits = api(f"repos/{ORG}/{repo}/commits?sha=main&per_page=1")
    if not commits:
        return ""
    return "Updated " + day(commits[0]["commit"]["committer"]["date"])


def on_page_markdown(markdown, page, config, files):
    if not (RELEASES_RE.search(markdown) or UPDATED_RE.search(markdown)):
        return markdown
    markdown = RELEASES_RE.sub(lambda m: releases(), markdown)
    return UPDATED_RE.sub(lambda m: updated(m.group(1)), markdown)
