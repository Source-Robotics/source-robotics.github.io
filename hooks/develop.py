"""The Develop page: every piece of software, integration and tool around the products, from develop.yml.

A page carries one marker, and the hook writes the whole list in its place, as cards:

    <!-- develop: cards -->    plain cards, three across, under a heading per group
    <!-- develop: covers -->   the same cards with a cover band in the group's colour and the entry's icon
    <!-- develop: rail -->     a panel per group on the left, its entries as compact cards on the right

Every entry carries `data-for` (the products it works with) and `data-status`; docs/javascripts/develop.js reads
them to show only what works with one product. A group's heading and lead carry `data-dev-head`, so the filter can
hide them with an empty group. Icons are the theme's own SVG files, put into the page as they are. The build stops
when develop.yml names a product, a status, a tone or an icon that does not exist, or an entry has no text.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import material
import yaml
from mkdocs.exceptions import PluginError

DATA = Path(__file__).resolve().parent.parent / "develop.yml"
ICONS = Path(material.__file__).resolve().parent / "templates" / ".icons"
MARKER = re.compile(r"<!--\s*develop:\s*(cards|covers|rail)\s*-->")
TONES = ("core-blue", "deep-teal", "indigo", "dusty-purple", "dark-gray")     # the brand's dark secondaries
e = html.escape


def load() -> dict:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    problems = []
    for group in data["groups"]:
        if group.get("tone") not in TONES:
            problems.append(f"{group.get('title')}: unknown tone {group.get('tone')!r}")
        for item in [group] + group["items"]:
            name = item.get("name") or item.get("title")
            if not (ICONS / f"{item.get('icon')}.svg").is_file():
                problems.append(f"{name}: no such icon {item.get('icon')!r}")
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


def icon(name: str, cls: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text(encoding="utf-8").strip()
    return f'<span class="{cls}" aria-hidden="true">{svg}</span>'


def pill(data: dict, item: dict) -> str:
    s = data["statuses"][item["status"]]
    return f'<span class="dev-pill dev-pill--{item["status"]}" title="{e(s["means"], quote=True)}">{e(s["label"])}</span>'


def chips(data: dict, item: dict) -> str:
    return "".join(f'<span class="dev-chip">{e(data["products"][p]["short"])}</span>' for p in item["for"])


def links(item: dict, cls: str = "") -> str:
    cls = f' class="{cls}"' if cls else ""
    out = "".join(f'<a{cls} href="{e(url, quote=True)}">{e(label)}</a>' for label, url in (item.get("links") or {}).items())
    return out or '<span class="dev-none">Not released yet</span>'


def note(item: dict, cls: str) -> str:
    parts = ([f'By {e(item["by"])}'] if item.get("by") else []) + ([f'Tested with {e(item["tested"])}'] if item.get("tested") else [])
    return f'<p class="{cls}">{" · ".join(parts)}</p>' if parts else ""


def attrs(item: dict) -> str:
    return f'data-for="{" ".join(item["for"])}" data-status="{item["status"]}"'


def heading(group: dict) -> str:
    """The group's heading and lead as Markdown, so the heading is in the page's table of contents."""
    shortcode = ":" + group["icon"].replace("/", "-") + ":"
    return (f'## {shortcode} {group["title"]} {{ #{group["id"]} data-dev-head="{group["id"]}" }}\n\n'
            f'{group["lead"]}\n{{ .dev-lead data-dev-head="{group["id"]}" }}\n\n')


def body(data: dict, item: dict) -> str:
    return (f'<p class="dev-card__name"><strong>{e(item["name"])}</strong></p>'
            f'<p class="dev-card__text">{e(item["text"])}</p>{note(item, "dev-card__meta")}'
            f'<p class="dev-card__chips">{chips(data, item)}</p>'
            f'<p class="dev-card__links">{links(item, "dev-btn")}</p>')


def cards_group(data: dict, group: dict) -> str:
    cards = [f'<article class="dev-entry dev-card" {attrs(item)}>'
             f'<p class="dev-card__top">{pill(data, item)}</p>{body(data, item)}</article>'
             for item in group["items"]]
    return heading(group) + f'<div class="dev-group dev-cards" data-group="{group["id"]}">\n' + "\n".join(cards) + "\n</div>"


def covers_group(data: dict, group: dict) -> str:
    cards = [f'<article class="dev-entry dev-card dev-card--cover" {attrs(item)}>'
             f'<div class="dev-card__band">{icon(item["icon"], "dev-icon")}{pill(data, item)}</div>'
             f'<div class="dev-card__body">{body(data, item)}</div></article>'
             for item in group["items"]]
    return (heading(group) + f'<div class="dev-group dev-cards dev-tone--{group["tone"]}" data-group="{group["id"]}">\n'
            + "\n".join(cards) + "\n</div>")


def rail_group(data: dict, group: dict) -> str:
    cards = [f'<article class="dev-entry dev-mini" {attrs(item)}>{icon(item["icon"], "dev-mini__icon")}'
             f'<div class="dev-mini__main">'
             f'<p class="dev-mini__name"><strong>{e(item["name"])}</strong>{pill(data, item)}</p>'
             f'<p class="dev-mini__text">{e(item["text"])}</p>{note(item, "dev-mini__meta")}'
             f'<p class="dev-mini__foot"><span class="dev-card__chips">{chips(data, item)}</span>'
             f'<span class="dev-mini__links">{links(item)}</span></p></div></article>'
             for item in group["items"]]
    return (f'<section class="dev-group dev-rail dev-tone--{group["tone"]}" data-group="{group["id"]}">\n'
            f'<div class="dev-rail__side">{icon(group["icon"], "dev-rail__icon")}'
            f'<h2 id="{group["id"]}">{e(group["title"])}</h2><p>{e(group["lead"])}</p></div>\n'
            f'<div class="dev-rail__cards">\n' + "\n".join(cards) + "\n</div>\n</section>")


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


GROUP = {"cards": cards_group, "covers": covers_group, "rail": rail_group}


def render(style: str) -> str:
    data = load()
    return "\n\n".join([top(data)] + [GROUP[style](data, group) for group in data["groups"]])


def on_page_markdown(markdown: str, **kwargs) -> str:
    return MARKER.sub(lambda m: render(m.group(1)), markdown)
