# shivamnegi92.github.io

Personal site of Shivam Negi: https://shivamnegi92.github.io

One static page (`index.html` + `css/site.css`), with no build step and no dependencies. It prints cleanly as a one-file CV.

Rule: every claim on the page must be backed by a public link or document. No unverified or confidential figures.

## Writing (guides and book reviews)

Articles live as Markdown-lite sources in `articles/*.md` and are rendered to
static pages under `writing/` by a stdlib-only builder:

```bash
python3 tools/build_articles.py          # rebuild writing/
python3 tools/build_articles.py --check  # validate sources and cover files
```

Diagrams are written inline as text blocks (`:::flow`, `:::layers`, `:::compare`,
`:::loop`, `:::seq`, `:::quadrant`, `:::tree`, `:::bars`) and rendered to
accessible, theme-aware SVG by `tools/diagrams.py`. Book covers are in
`img/books/` (see the README there).
