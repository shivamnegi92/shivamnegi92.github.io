"""Tiny text-to-SVG diagram renderer (stdlib only).

Each renderer takes the lines of a ``:::kind Caption`` block and returns SVG
markup. Colors come from CSS classes in articles.css so light/dark stay consistent.

Kinds: flow, layers, compare, loop, seq, quadrant, tree, bars.
"""
from __future__ import annotations

import math
from html import escape

W = 760          # viewBox width
CHAR = 7.1       # approx px per char at 13px
LINE = 17        # line height for labels


def wrap(text: str, width_px: float) -> list[str]:
    limit = max(4, int(width_px / CHAR))
    words, lines, cur = text.split(), [], ""
    for word in words:
        if len(cur) + len(word) + (1 if cur else 0) <= limit:
            cur = f"{cur} {word}".strip()
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def _style(label: str) -> tuple[str, str]:
    """Trailing * = accent, ! = danger, ~ = muted."""
    for mark, cls in (("*", "acc"), ("!", "bad"), ("~", "dim")):
        if label.endswith(mark):
            return label[:-1].strip(), cls
    return label.strip(), "node"


def _text(x: float, y: float, lines: list[str], cls: str = "t", anchor: str = "middle") -> str:
    top = y - (len(lines) - 1) * LINE / 2
    spans = "".join(
        f'<tspan x="{x:.1f}" y="{top + i * LINE:.1f}">{escape(line)}</tspan>' for i, line in enumerate(lines)
    )
    return f'<text class="{cls}" text-anchor="{anchor}" dominant-baseline="middle">{spans}</text>'


def _box(x, y, w, h, label, cls) -> str:
    lines = wrap(label, w - 16)
    return (f'<rect class="b-{cls}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10"/>'
            + _text(x + w / 2, y + h / 2, lines, f"t t-{cls}"))


def _arrow(x1, y1, x2, y2, dashed=False) -> str:
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return f'<line class="arr" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"{dash} marker-end="url(#ah)"/>'


def _svg(h: float, body: str, title: str, uid: str) -> str:
    return (f'<svg viewBox="0 0 {W} {h:.0f}" role="img" aria-labelledby="{uid}" class="dg" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="{uid}">{escape(title)}</title>'
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'
            f"{body}</svg>")


# ---------------------------------------------------------------- renderers
def flow(lines, title, uid):
    rows = []
    for line in lines:
        label, _, rest = line.partition(":") if ":" in line.split("->")[0] else ("", "", line)
        rows.append((label.strip(), [n for n in (rest or line).split("->")]))
    gap, pad, body, y = 34, 12, [], 10
    for label, nodes in rows:
        if label:
            body.append(_text(pad, y + 8, [label.upper()], "t t-cap", "start"))
            y += 20
        n = len(nodes)
        bw = (W - 2 * pad - gap * (n - 1)) / n
        styled = [_style(x) for x in nodes]
        bh = max(len(wrap(t, bw - 16)) for t, _ in styled) * LINE + 22
        for i, (text, cls) in enumerate(styled):
            x = pad + i * (bw + gap)
            body.append(_box(x, y, bw, bh, text, cls))
            if i < n - 1:
                body.append(_arrow(x + bw + 3, y + bh / 2, x + bw + gap - 4, y + bh / 2))
        y += bh + 18
    return _svg(y, "".join(body), title, uid)


def layers(lines, title, uid):
    body, y, pad = [], 8, 12
    for i, line in enumerate(lines):
        name, _, sub = line.partition("|")
        name, cls = _style(name)
        sub_lines = wrap(sub.strip(), W - 2 * pad - 230) if sub.strip() else []
        h = max(44, len(sub_lines) * LINE + 22)
        body.append(f'<rect class="b-layer l{i % 6} b-{cls}" x="{pad}" y="{y}" width="{W - 2 * pad}" height="{h}" rx="10"/>')
        body.append(_text(pad + 16, y + h / 2, [name], "t t-strong", "start"))
        if sub_lines:
            body.append(_text(pad + 230, y + h / 2, sub_lines, "t", "start"))
        y += h + 8
    return _svg(y, "".join(body), title, uid)


def compare(lines, title, uid):
    panels, cur = [], None
    for line in lines:
        if line.startswith("#"):
            cur = [line.lstrip("# ").strip(), []]
            panels.append(cur)
        elif cur is not None:
            cur[1].append(line.lstrip("- ").strip())
    n, pad, gap = len(panels), 12, 16
    pw = (W - 2 * pad - gap * (n - 1)) / n
    wrapped = [[wrap(item, pw - 40) for item in items] for _, items in panels]
    h = max(sum(len(w) * LINE + 10 for w in items) for items in wrapped) + 70
    body = []
    for i, ((head, _), items) in enumerate(zip(panels, wrapped)):
        x = pad + i * (pw + gap)
        body.append(f'<rect class="b-panel" x="{x:.1f}" y="8" width="{pw:.1f}" height="{h:.1f}" rx="12"/>')
        body.append(f'<rect class="b-head p{i}" x="{x:.1f}" y="8" width="{pw:.1f}" height="40" rx="12"/>')
        body.append(f'<rect class="b-head p{i}" x="{x:.1f}" y="30" width="{pw:.1f}" height="18"/>')
        body.append(_text(x + pw / 2, 28, [head], "t t-head"))
        y = 66
        for item in items:
            body.append(f'<circle class="dot p{i}" cx="{x + 18:.1f}" cy="{y + 1:.1f}" r="4"/>')
            body.append(_text(x + 30, y + (len(item) - 1) * LINE / 2, item, "t", "start"))
            y += len(item) * LINE + 10
    return _svg(h + 16, "".join(body), title, uid)


def loop(lines, title, uid):
    n = len(lines)
    cx, cy, rx, ry = W / 2, 170, 270, 120
    bw, bh, body, pts = 150, 52, [], []
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    body.append(f'<ellipse class="ring" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>')
    for i, (x, y) in enumerate(pts):
        nx, ny = pts[(i + 1) % n]
        mx, my = (x + nx) / 2, (y + ny) / 2
        ang = math.atan2(ny - y, nx - x)
        body.append(f'<path class="ah big" d="M{mx + 9 * math.cos(ang):.1f} {my + 9 * math.sin(ang):.1f} '
                    f'L{mx - 7 * math.cos(ang) + 6 * math.sin(ang):.1f} {my - 7 * math.sin(ang) - 6 * math.cos(ang):.1f} '
                    f'L{mx - 7 * math.cos(ang) - 6 * math.sin(ang):.1f} {my - 7 * math.sin(ang) + 6 * math.cos(ang):.1f}z"/>')
    for i, (x, y) in enumerate(pts):
        text, cls = _style(lines[i])
        body.append(_box(x - bw / 2, y - bh / 2, bw, bh, f"{i + 1}. {text}", cls))
    return _svg(cy + ry + 40, "".join(body), title, uid)


def seq(lines, title, uid):
    actors = [a.strip() for a in lines[0].split(":", 1)[1].split(",")]
    msgs = lines[1:]
    pad, n = 12, len(actors)
    col = (W - 2 * pad) / n
    xs = [pad + col * (i + 0.5) for i in range(n)]
    top, step = 56, 46
    h = top + step * len(msgs) + 30
    body = []
    for x, a in zip(xs, actors):
        body.append(f'<line class="life" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{h - 10:.1f}"/>')
        body.append(_box(x - col / 2 + 8, 8, col - 16, 40, a, "acc"))
    for i, m in enumerate(msgs):
        dashed = "-->" in m
        left, _, label = m.partition(":")
        a, b = [s.strip() for s in left.replace("-->", "->").split("->")]
        y = top + 26 + i * step
        x1, x2 = xs[actors.index(a)], xs[actors.index(b)]
        if x1 == x2:
            body.append(f'<path class="arr" fill="none" d="M{x1} {y - 8} h40 v16 h-36" marker-end="url(#ah)"/>')
            body.append(_text(x1 + 48, y, [label.strip()], "t t-sm", "start"))
        else:
            off = 4 if x2 > x1 else -4
            body.append(_arrow(x1 + off, y, x2 - off, y, dashed))
            body.append(_text((x1 + x2) / 2, y - 11, [label.strip()], "t t-sm"))
    return _svg(h, "".join(body), title, uid)


def quadrant(lines, title, uid):
    cfg, pts = {}, []
    for line in lines:
        key, _, val = line.partition(":")
        if key.strip() == "pt":
            label, _, xy = val.partition("@")
            x, y = (float(v) for v in xy.split(","))
            pts.append((*_style(label), x, y))
        else:
            cfg[key.strip()] = [v.strip() for v in val.split("|")]
    L, T, S = 150, 20, 300
    PW = S * 1.55
    body = [f'<rect class="b-panel" x="{L}" y="{T}" width="{PW}" height="{S}" rx="8"/>',
            f'<line class="life" x1="{L + PW / 2}" y1="{T}" x2="{L + PW / 2}" y2="{T + S}"/>',
            f'<line class="life" x1="{L}" y1="{T + S / 2}" x2="{L + PW}" y2="{T + S / 2}"/>']
    xl, yl = cfg.get("x", ["", ""]), cfg.get("y", ["", ""])
    body.append(_text(L, T + S + 18, [xl[0]], "t t-sm", "start"))
    body.append(_text(L + PW, T + S + 18, [xl[-1] + " \u2192"], "t t-sm", "end"))
    body.append(_text(L - 10, T + S - 8, wrap(yl[0], 130), "t t-sm", "end"))
    body.append(_text(L - 10, T + 12, wrap("\u2191 " + yl[-1], 130), "t t-sm", "end"))
    for label, cls, x, y in pts:
        px, py = L + x * PW, T + (1 - y) * S
        body.append(f'<circle class="pt pt-{cls}" cx="{px:.1f}" cy="{py:.1f}" r="8"/>')
        anchor = "end" if x > 0.7 else "start"
        body.append(_text(px + (-14 if anchor == "end" else 14), py, [label], f"t t-{cls}x", anchor))
    return _svg(T + S + 34, "".join(body), title, uid)


def tree(lines, title, uid):
    nodes = []  # (depth, label, parent_index)
    stack = []
    for line in lines:
        depth = (len(line) - len(line.lstrip(" "))) // 2
        while stack and stack[-1][0] >= depth:
            stack.pop()
        parent = stack[-1][1] if stack else None
        nodes.append([depth, line.strip(), parent, 0.0])
        stack.append((depth, len(nodes) - 1))
    maxd = max(n[0] for n in nodes)
    pad, gap = 12, 40
    bw = (W - 2 * pad - gap * maxd) / (maxd + 1)
    children = {i: [j for j, n in enumerate(nodes) if n[2] == i] for i in range(len(nodes))}
    leaves = [i for i in range(len(nodes)) if not children[i]]
    bh, rowh = 44, 58
    for k, i in enumerate(leaves):
        nodes[i][3] = 14 + k * rowh + bh / 2

    def place(i):
        if children[i]:
            ys = [place(c) for c in children[i]]
            nodes[i][3] = sum(ys) / len(ys)
        return nodes[i][3]

    for i, n in enumerate(nodes):
        if n[2] is None:
            place(i)
    body = []
    for i, (d, label, parent, y) in enumerate(nodes):
        x = pad + d * (bw + gap)
        if parent is not None:
            px = pad + nodes[parent][0] * (bw + gap) + bw
            py = nodes[parent][3]
            body.append(f'<path class="arr" fill="none" d="M{px:.1f} {py:.1f} H{px + gap / 2:.1f} V{y:.1f} H{x - 4:.1f}" marker-end="url(#ah)"/>')
        text, cls = _style(label)
        body.append(_box(x, y - bh / 2, bw, bh, text, cls))
    return _svg(len(leaves) * rowh + 16, "".join(body), title, uid)


def bars(lines, title, uid):
    rows = []
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        label, cls = _style(parts[0])
        rows.append((label, cls, float(parts[1]), parts[2] if len(parts) > 2 else ""))
    top = max(r[2] for r in rows) or 1
    L, pad, bh, gap = 220, 12, 22, 14
    span = W - L - pad - 120
    body = []
    for i, (label, cls, val, note) in enumerate(rows):
        y = 10 + i * (bh + gap)
        body.append(_text(L - 12, y + bh / 2, [label], "t", "end"))
        body.append(f'<rect class="track" x="{L}" y="{y}" width="{span}" height="{bh}" rx="6"/>')
        body.append(f'<rect class="bar bar-{cls}" x="{L}" y="{y}" width="{span * val / top:.1f}" height="{bh}" rx="6"/>')
        body.append(_text(L + span + 10, y + bh / 2, [note or f"{val:g}"], "t t-strong", "start"))
    return _svg(10 + len(rows) * (bh + gap), "".join(body), title, uid)


RENDERERS = {f.__name__: f for f in (flow, layers, compare, loop, seq, quadrant, tree, bars)}


def render(kind: str, lines: list[str], title: str, uid: str) -> str:
    if kind not in RENDERERS:
        raise ValueError(f"unknown diagram kind '{kind}' (have {', '.join(RENDERERS)})")
    svg = RENDERERS[kind]([l for l in lines if l.strip()], title, uid)
    # unique marker id per figure: several diagrams share one page
    return svg.replace('id="ah"', f'id="ah-{uid}"').replace("url(#ah)", f"url(#ah-{uid})")
