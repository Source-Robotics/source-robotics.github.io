"""The Develop page: every piece of software, integration and tool around the products, from develop.yml.

A page carries one marker, and the hook writes the whole list in its place:

    <!-- develop: list -->     one row per entry: name, status, text, what it works with, links
    <!-- develop: cards -->    the same entries as cards
    <!-- develop: matrix -->   a table per group with a column per product

Each group becomes a `## heading` (so it is in the page's table of contents) followed by its entries as HTML. Every
entry carries `data-for` (the products it works with) and `data-status`; docs/javascripts/develop.js reads them to
show only what works with one product. The build stops when develop.yml names a product or a status it does not
offer, or an entry has no text.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import yaml
from mkdocs.exceptions import PluginError

DATA = Path(__file__).resolve().parent.parent / "develop.yml"
MARKER = re.compile(r"<!--\s*develop:\s*(list|cards|matrix)\s*-->")
e = html.escape


def load() -> dict:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    problems = []
    for group in data["groups"]:
        for item in group["items"]:
            name = item.get("name", "(no name)")
            if not item.get("text"):
                problems.append(f"{name}: no text")
            if item.get("status") not in data["statuses"]:
                problems.append(f"{name}: unknown status {item.get('status')!r}")
            unknown = [p for p in item.get("for") or [] if p not in data["products"]]
            if unknown or not item.get("for"):
                problems.append(f"{name}: `for` is empty or names an unknown product {unknown}")
    if problems:
        raise PluginError("develop.yml:\n  " + "\n  ".join(problems))
    return data


def pill(data: dict, item: dict) -> str:
    s = data["statuses"][item["status"]]
    return f'<span class="dev-pill dev-pill--{item["status"]}" title="{e(s["means"], quote=True)}">{e(s["label"])}</span>'


def chips(data: dict, item: dict) -> str:
    return "".join(f'<span class="dev-chip">{e(data["products"][p]["short"])}</span>' for p in item["for"])


def links(item: dict, cls: str = "") -> str:
    cls = f' class="{cls}"' if cls else ""
    return "".join(f'<a{cls} href="{e(url, quote=True)}">{e(label)}</a>' for label, url in (item.get("links") or {}).items())


def notes(item: dict) -> list[str]:
    out = []
    if item.get("by"):
        out.append(f'By {e(item["by"])}')
    if item.get("tested"):
        out.append(f'Tested with {e(item["tested"])}')
    return out


def attrs(item: dict) -> str:
    return f'data-for="{" ".join(item["for"])}" data-status="{item["status"]}"'


def list_group(data: dict, group: dict) -> str:
    rows = []
    for item in group["items"]:
        meta = chips(data, item) + "".join(f"<span>{n}</span>" for n in notes(item))
        link = links(item) or '<span class="dev-none">Not released yet</span>'
        rows.append(
            f'<article class="dev-entry dev-item" {attrs(item)}>'
            f'<div class="dev-item__main">'
            f'<p class="dev-item__name"><strong>{e(item["name"])}</strong>{pill(data, item)}</p>'
            f'<p class="dev-item__text">{e(item["text"])}</p>'
            f'<p class="dev-item__meta">{meta}</p></div>'
            f'<p class="dev-item__links">{link}</p></article>')
    return f'<div class="dev-group dev-list" data-group="{group["id"]}">\n' + "\n".join(rows) + "\n</div>"


def cards_group(data: dict, group: dict) -> str:
    cards = []
    for item in group["items"]:
        note = " · ".join(notes(item))
        note = f'<p class="dev-card__meta">{note}</p>' if note else ""
        link = links(item, "dev-btn") or '<span class="dev-none">Not released yet</span>'
        cards.append(
            f'<article class="dev-entry dev-card" {attrs(item)}>'
            f'<p class="dev-card__top">{pill(data, item)}</p>'
            f'<p class="dev-card__name"><strong>{e(item["name"])}</strong></p>'
            f'<p class="dev-card__text">{e(item["text"])}</p>{note}<p class="dev-card__chips">{chips(data, item)}</p>'
            f'<p class="dev-card__links">{link}</p></article>')
    return f'<div class="dev-group dev-cards" data-group="{group["id"]}">\n' + "\n".join(cards) + "\n</div>"


def matrix_group(data: dict, group: dict) -> str:
    products = data["products"]
    head = "".join(f'<th class="dev-col" data-col="{p}" scope="col">{e(v["short"])}</th>' for p, v in products.items())
    cols = '<col class="dev-c-name">' + '<col class="dev-c-dot">' * len(products) + '<col class="dev-c-status"><col class="dev-c-links">'
    rows = []
    for item in group["items"]:
        note = " · ".join(notes(item))
        note = f'<span class="dev-row__meta">{note}</span>' if note else ""
        dots = "".join(
            f'<td class="dev-col" data-col="{p}">'
            + (f'<span class="dev-dot" role="img" aria-label="works with {e(v["label"], quote=True)}"></span>' if p in item["for"] else "")
            + "</td>" for p, v in products.items())
        link = links(item) or '<span class="dev-none">Not released yet</span>'
        rows.append(
            f'<tr class="dev-entry dev-row" {attrs(item)}>'
            f'<th scope="row"><strong>{e(item["name"])}</strong><span class="dev-row__text">{e(item["text"])}</span>{note}</th>'
            f'{dots}<td class="dev-row__status">{pill(data, item)}</td><td class="dev-row__links">{link}</td></tr>')
    return (f'<div class="dev-group dev-matrix-wrap" data-group="{group["id"]}">\n<table class="dev-matrix">'
            f'<colgroup>{cols}</colgroup>\n<thead><tr><td></td>{head}'
            f'<th scope="col">Status</th><th scope="col">Links</th></tr></thead>\n<tbody>\n'
            + "\n".join(rows) + "\n</tbody></table>\n</div>")


def top(data: dict) -> str:
    buttons = '<button type="button" class="dev-filter__btn" data-for="">Everything</button>' + "".join(
        f'<button type="button" class="dev-filter__btn" data-for="{p}">{e(v["label"])}</button>'
        for p, v in data["products"].items())
    legend = "".join(
        f'<span class="dev-legend__item"><span class="dev-pill dev-pill--{k}">{e(s["label"])}</span>{e(s["means"])}</span>'
        for k, s in data["statuses"].items())
    return ('<div class="dev-top">\n'
            f'<div class="dev-filter" role="group" aria-label="Show what works with" hidden>'
            f'<span class="dev-filter__label">Works with</span>{buttons}</div>\n'
            '<p class="dev-count" aria-live="polite" hidden></p>\n'
            f'<p class="dev-legend">{legend}</p>\n</div>')


GROUP = {"list": list_group, "cards": cards_group, "matrix": matrix_group}


def render(style: str) -> str:
    data = load()
    parts = [top(data)]
    for group in data["groups"]:
        icon = f':{group["icon"]}: ' if style == "cards" and group.get("icon") else ""
        parts.append(f'## {icon}{group["title"]} {{ #{group["id"]} }}')
        parts.append(f'{group["lead"]}\n{{ .dev-lead }}')
        parts.append(GROUP[style](data, group))
    return "\n\n".join(parts)


def on_page_markdown(markdown: str, **kwargs) -> str:
    return MARKER.sub(lambda m: render(m.group(1)), markdown)
