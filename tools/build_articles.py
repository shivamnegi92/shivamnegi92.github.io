"""Build /writing/ from articles/*.md (stdlib only).

Source format:
    ---
    title: ...
    slug: ...            (defaults to file stem)
    kind: guide | review
    date: 2026-10-01
    order: 1             (position within its kind)
    summary: one line
    tags: a, b
    book: Title | Author | Publisher Year | ISBN | img/books/x.jpg   (reviews only)
    verdict: one line                                                (reviews only)
    rating: 4.5                                                      (reviews only)
    ---
    Markdown-lite body: #/##/### headings, paragraphs, - lists, 1. lists,
    > quotes, ```code```, **bold**, *italic*, `code`, [text](url),
    | tables |, :::kind Caption ... ::: diagram blocks, !!! callouts.

Usage: python3 tools/build_articles.py [--check]
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from email.utils import format_datetime
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from diagrams import render  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "articles"
OUT = ROOT / "writing"
SITE = "https://shivamnegi92.github.io"


# ---------------------------------------------------------------- parsing
def parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise ValueError(f"{path.name}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip()
    for req in ("title", "kind", "date", "summary"):
        if not meta.get(req):
            raise ValueError(f"{path.name}: front matter needs '{req}'")
    meta.setdefault("slug", path.stem)
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    if meta["kind"] == "review":
        parts = [p.strip() for p in meta["book"].split("|")]
        meta["book"] = dict(zip(("title", "author", "pub", "isbn", "img"), parts))
    meta["body"] = m.group(2)
    return meta


def inline(s: str) -> str:
    s = escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def body_html(md: str, slug: str) -> tuple[str, list[tuple[str, str]], int]:
    out, toc, lines, i, fig = [], [], md.splitlines(), 0, 0
    para: list[str] = []

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush(); i += 1; continue
        if s.startswith(":::"):
            flush()
            kind, _, caption = s[3:].partition(" ")
            block = []
            i += 1
            while not lines[i].strip().startswith(":::"):
                block.append(lines[i].rstrip()); i += 1
            fig += 1
            svg = render(kind, block, caption, f"{slug}-f{fig}")
            out.append(f'<figure class="diagram"><div class="dg-wrap" tabindex="0" role="region" '
                       f'aria-label="Figure {fig}: {escape(caption)}">{svg}</div>'
                       f'<figcaption><span>Figure {fig}</span> {inline(caption)}'
                       f'<span class="dg-hint"> (swipe to see the full diagram)</span></figcaption></figure>')
            i += 1; continue
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            block = []
            i += 1
            while not lines[i].strip().startswith("```"):
                block.append(lines[i]); i += 1
            label = f'<span class="lang">{escape(lang)}</span>' if lang else ""
            region_label = escape(lang or "code")
            out.append(f'<pre class="code" tabindex="0" role="region" aria-label="Scrollable {region_label} block">{label}<code>{escape(chr(10).join(block))}</code></pre>')
            i += 1; continue
        if s.startswith("!!!"):
            flush()
            kind, _, text = s[3:].strip().partition(" ")
            block = [text]
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i].strip()); i += 1
            out.append(f'<aside class="callout c-{kind}"><strong>{escape(kind.title())}</strong> {inline(" ".join(block))}</aside>')
            continue
        m = re.match(r"(#{2,3}) (.*)", s)
        if m:
            flush()
            level, text = len(m.group(1)), m.group(2)
            hid = slugify(text)
            if level == 2:
                toc.append((hid, text))
            out.append(f'<h{level} id="{hid}">{inline(text)}</h{level}>')
            i += 1; continue
        if s.startswith("> "):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip()[1:].strip()); i += 1
            out.append(f"<blockquote>{inline(' '.join(block))}</blockquote>")
            continue
        if s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, rest = rows[0], [r for r in rows[1:] if not set("".join(r)) <= set("-: ")]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rest)
            out.append(f'<div class="table" tabindex="0" role="region" aria-label="Scrollable data table"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue
        if re.match(r"(- |\d+\. )", s):
            flush()
            ordered = s[0].isdigit()
            items = []
            while i < len(lines) and re.match(r"\s*(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^\s*(- |\d+\. )", "", lines[i])); i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        para.append(s)
        i += 1
    flush()
    return "\n".join(out), toc, fig


# ---------------------------------------------------------------- templates
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Shivam Negi</title>
<meta name="description" content="{desc}">
<meta name="author" content="Shivam Negi">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="theme-color" content="#0b1020">
<link rel="alternate" type="application/rss+xml" title="Shivam Negi: Writing" href="{base}writing/feed.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 rx=%2714%27 fill=%27%235b6cf6%27/%3E%3Ctext x=%2732%27 y=%2742%27 font-family=%27Arial%27 font-size=%2728%27 font-weight=%27700%27 fill=%27white%27 text-anchor=%27middle%27%3ESN%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="{base}css/articles.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="bar"><div class="wrap">
  <a class="brand" href="{base}"><span class="mono" aria-hidden="true">SN</span>Shivam Negi</a>
  <nav aria-label="Primary"><a href="{base}#research">Research</a><a href="{base}writing/">Writing</a><a href="{base}writing/#reviews">Book reviews</a><a href="{base}#contact">Contact</a></nav>
</div></header>
"""

FOOT = """<footer class="foot"><div class="wrap">
<p>&copy; {year} Shivam Negi. Views are my own and do not represent any employer. Book covers are shown for identification and review purposes. <a href="{base}writing/feed.xml">RSS</a></p>
</div></footer>
<script src="{base}js/articles.js"></script>
</body></html>
"""


def stars(rating: float) -> str:
    full = int(rating)
    half = rating - full >= 0.5
    s = "\u2605" * full + ("\u00bd" if half else "") + "\u2606" * (5 - full - (1 if half else 0))
    return f'<span class="stars" aria-label="{rating} out of 5">{s}</span>'


def read_minutes(md: str) -> int:
    return max(3, round(len(re.findall(r"\w+", md)) / 230))


def article_page(a: dict, prev_a: dict | None, next_a: dict | None) -> str:
    html, toc, figs = body_html(a["body"], a["slug"])
    url = f"{SITE}/writing/{a['slug']}/"
    minutes = read_minutes(a["body"])
    kind_label = "Book review" if a["kind"] == "review" else "Guide"
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"%s","headline":%s,'
          '"datePublished":"%s","author":{"@type":"Person","name":"Shivam Negi","url":"%s/"}%s}</script>') % (
        "Review" if a["kind"] == "review" else "TechArticle", _json(a["title"]), a["date"], SITE,
        (',"itemReviewed":{"@type":"Book","name":%s,"author":%s,"isbn":"%s"},"reviewRating":{"@type":"Rating","ratingValue":"%s","bestRating":"5"}'
         % (_json(a["book"]["title"]), _json(a["book"]["author"]), a["book"]["isbn"], a.get("rating", "")))
        if a["kind"] == "review" else "")
    image = f"{SITE}/{a['book']['img']}" if a["kind"] == "review" else f"{SITE}/img/about.jpg"
    head = HEAD.format(title=escape(a["title"]), desc=escape(a["summary"]), url=url, ogtype="article",
                       base="../../", ld=ld, image=image)
    hero_book = ""
    if a["kind"] == "review":
        b = a["book"]
        hero_book = f"""<div class="bookcard">
  <figure class="cover3d"><img src="../../{b['img']}" alt="Cover of {escape(b['title'])} by {escape(b['author'])}" width="220" height="330" loading="eager"></figure>
  <dl>
    <dt>Book</dt><dd><cite>{escape(b['title'])}</cite></dd>
    <dt>Author</dt><dd>{escape(b['author'])}</dd>
    <dt>Publisher</dt><dd>{escape(b['pub'])}</dd>
    <dt>ISBN</dt><dd>{escape(b['isbn'])}</dd>
    <dt>My rating</dt><dd>{stars(float(a['rating']))} <b>{a['rating']}/5</b></dd>
  </dl>
  <p class="verdict"><span>Verdict</span>{inline(a['verdict'])}</p>
</div>"""
    toc_html = "".join(f'<li><a href="#{h}">{escape(t)}</a></li>' for h, t in toc)
    tags = "".join(f"<li>{escape(t)}</li>" for t in a["tags"])
    nav = ""
    if prev_a or next_a:
        nav = '<nav class="pn" aria-label="More articles">'
        if prev_a:
            nav += f'<a href="../{prev_a["slug"]}/"><span>Previous</span>{escape(prev_a["title"])}</a>'
        if next_a:
            nav += f'<a class="next" href="../{next_a["slug"]}/"><span>Next</span>{escape(next_a["title"])}</a>'
        nav += "</nav>"
    return head + f"""<main id="main">
<article>
  <header class="ahero {a['kind']}"><div class="wrap">
    <p class="crumbs"><a href="../">Writing</a> / {kind_label}</p>
    <h1>{inline(a['title'])}</h1>
    <p class="dek">{inline(a['summary'])}</p>
    <p class="meta"><time datetime="{a['date']}">{_pretty(a['date'])}</time> &middot; {minutes} min read &middot; {figs} diagrams</p>
    <ul class="tags">{tags}</ul>
    {hero_book}
  </div></header>
  <div class="wrap layout">
    <aside class="toc" aria-label="On this page"><p>On this page</p><ol>{toc_html}</ol></aside>
    <div class="prose">{html}
      <div class="author"><img src="../../img/about.jpg" alt="" width="56" height="56"><p><strong>Shivam Negi</strong> is an AI engineer and Principal Data Scientist who works on evaluating voice agents, small language models, and applied ML. <a href="../../">More about me</a></p></div>
      {nav}
    </div>
  </div>
</article>
</main>
""" + FOOT.format(year=date.today().year, base="../../")


def _json(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _rfc822(d: str) -> str:
    return format_datetime(datetime.fromisoformat(d + "T12:00:00+00:00"))


def _pretty(d: str) -> str:
    y, m, dd = d.split("-")
    return f"{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(m) - 1]} {int(dd)}, {y}"


def card(a: dict) -> str:
    tags = "".join(f"<li>{escape(t)}</li>" for t in a["tags"][:3])
    if a["kind"] == "review":
        b = a["book"]
        return f"""<li class="rcard"><a href="{a['slug']}/">
  <img src="../{b['img']}" alt="" width="120" height="180" loading="lazy">
  <div><span class="kicker">Book review &middot; {stars(float(a['rating']))}</span>
  <h3>{escape(b['title'])}</h3><p class="by">{escape(b['author'])}</p>
  <p>{inline(a['verdict'])}</p><ul class="tags">{tags}</ul></div></a></li>"""
    return f"""<li class="gcard"><a href="{a['slug']}/">
  <span class="kicker">Guide &middot; {read_minutes(a['body'])} min</span>
  <h3>{escape(a['title'])}</h3><p>{inline(a['summary'])}</p><ul class="tags">{tags}</ul></a></li>"""


def index_page(arts: list[dict]) -> str:
    guides = [a for a in arts if a["kind"] == "guide"]
    reviews = [a for a in arts if a["kind"] == "review"]
    head = HEAD.format(title="Writing", desc="Diagram-heavy guides on AI systems and reviews of the books that shaped them.",
                       url=f"{SITE}/writing/", ogtype="website", base="../", ld="",
                       image=f"{SITE}/img/about.jpg")
    return head + f"""<main id="main">
<header class="ahero idx"><div class="wrap">
  <p class="crumbs"><a href="../">Home</a> / Writing</p>
  <h1>Writing</h1>
  <p class="dek">Field notes from building AI systems in production. How-to and why-it-works guides drawn as diagrams, plus reviews of the books every AI and data engineer should read.</p>
  <p class="meta">{len(guides)} guides &middot; {len(reviews)} book reviews &middot; <a href="feed.xml">RSS</a></p>
</div></header>
<div class="wrap">
  <section aria-labelledby="g-h"><h2 id="g-h" class="sec">Guides</h2><ul class="ggrid">{''.join(card(a) for a in guides)}</ul></section>
  <section id="reviews" aria-labelledby="r-h"><h2 id="r-h" class="sec">Book reviews</h2><ul class="rgrid">{''.join(card(a) for a in reviews)}</ul></section>
</div>
</main>
""" + FOOT.format(year=date.today().year, base="../")


def feed(arts: list[dict]) -> str:
    items = "".join(
        f"<item><title>{escape(a['title'])}</title><link>{SITE}/writing/{a['slug']}/</link>"
        f"<guid>{SITE}/writing/{a['slug']}/</guid><pubDate>{_rfc822(a['date'])}</pubDate>"
        f"<description>{escape(a['summary'])}</description></item>" for a in arts)
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Shivam Negi: Writing</title>'
            f"<link>{SITE}/writing/</link><description>Guides and book reviews on AI systems.</description>{items}</channel></rss>\n")


def build(check: bool = False) -> list[str]:
    arts = sorted((parse(p) for p in SRC.glob("*.md")),
                  key=lambda a: (a["kind"] != "guide", int(a.get("order", 99)), a["slug"]))
    errors = []
    slugs = [a["slug"] for a in arts]
    if len(set(slugs)) != len(slugs):
        errors.append("duplicate slugs")
    for a in arts:
        if a["kind"] == "review" and not (ROOT / a["book"]["img"]).exists():
            errors.append(f"{a['slug']}: missing cover {a['book']['img']}")
    if check:
        return errors
    OUT.mkdir(exist_ok=True)
    for kind in ("guide", "review"):
        group = [a for a in arts if a["kind"] == kind]
        for i, a in enumerate(group):
            d = OUT / a["slug"]
            d.mkdir(exist_ok=True)
            prev_a = group[i - 1] if i > 0 else None
            next_a = group[i + 1] if i + 1 < len(group) else None
            (d / "index.html").write_text(article_page(a, prev_a, next_a), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(arts), encoding="utf-8")
    (OUT / "feed.xml").write_text(feed(arts), encoding="utf-8")
    print(f"Built {len(arts)} articles into {OUT.relative_to(ROOT)}/")
    return errors


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    errs = build(ap.parse_args().check)
    if errs:
        print("\n".join(errs), file=sys.stderr)
        raise SystemExit(1)
