"""Generate the README's timeline and Gambit SVGs: python3 assets/generate.py"""

from html import escape
from pathlib import Path

OUT = Path(__file__).parent

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
THEMES = {
    "light": dict(fg="#1f2328", muted="#59636e", line="#d1d9e0", accent="#0969da", soft="#b6d7ff", node="#f6f8fa"),
    "dark": dict(fg="#f0f6fc", muted="#9198a1", line="#3d444d", accent="#4493f8", soft="#1f3a5f", node="#151b23"),
}
SIZES = {"": 840, "-narrow": 420}
CHAR = 7.0  # rough average advance at 13px, used only to keep labels inside the frame


def svg(w: float, h: float, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h:.0f}" viewBox="0 0 {w} {h:.0f}" role="img" aria-label="{title}">'
        f"<title>{title}</title>"
        f'<g font-family="{FONT}" font-size="13">{body}</g></svg>\n'
    )


ROLES = [
    ("Symonds & Son", "Founder", 2011.0, 2026.8, "soft"),
    ("M1 Finance", "CISO", 2015.58, 2019.75, "accent"),
    ("Capital Markets Gateway", "DevOps & CISO", 2019.83, 2020.96, "accent"),
    ("CrossnoKaye", "Principal Engineer, Senior Manager", 2021.0, 2026.1, "accent"),
    ("Attain", "Director of SRE", 2026.17, 2026.8, "accent"),
]


def timeline(theme: str, w: float) -> str:
    c = THEMES[theme]
    narrow = w < 600
    pad = 6
    y0, y1 = 2011.0, 2026.8

    def x(year: float) -> float:
        return pad + (year - y0) / (y1 - y0) * (w - 2 * pad)

    row = 36
    parts: list[str] = []
    for i, (name, role, a, b, kind) in enumerate(ROLES):
        ry = 4 + i * row
        xa, xb = x(a), x(b)
        label_len = len(name) if narrow else len(name) + len(role) + 5
        if xa + label_len * CHAR > w - pad:
            tx, anchor = xb, "end"
        else:
            tx, anchor = xa, "start"
        role_span = "" if narrow else f'<tspan fill="{c["muted"]}"> · {escape(role)}</tspan>'
        name_span = f'<tspan fill="{c["fg"]}" font-weight="600">{escape(name)}</tspan>'
        parts.append(f'<text x="{tx:.1f}" y="{ry + 14}" text-anchor="{anchor}">{name_span}{role_span}</text>')
        parts.append(f'<rect x="{xa:.1f}" y="{ry + 21}" width="{xb - xa:.1f}" height="7" rx="3.5" fill="{c[kind]}"/>')
    axis_y = 4 + row * len(ROLES) + 6
    parts.append(f'<line x1="{pad}" y1="{axis_y}" x2="{w - pad}" y2="{axis_y}" stroke="{c["line"]}"/>')
    for yr in range(2011, 2027):
        gx = x(yr)
        major = (yr - 2011) % 5 == 0
        parts.append(f'<line x1="{gx:.1f}" y1="{axis_y}" x2="{gx:.1f}" y2="{axis_y + (6 if major else 3)}" stroke="{c["line"]}"/>')
        if major and yr < 2026:
            anchor = "start" if yr == 2011 else "middle"
            parts.append(f'<text x="{gx:.1f}" y="{axis_y + 20}" fill="{c["muted"]}" font-size="12" text-anchor="{anchor}">{yr}</text>')
    parts.append(f'<text x="{w - pad}" y="{axis_y + 20}" fill="{c["muted"]}" font-size="12" text-anchor="end">now</text>')
    return svg(w, axis_y + 28, "".join(parts), "Career timeline, 2011 to present")


STEPS = [("Contract", True), ("Build", False), ("Review", False), ("Release", False), ("Report", True)]


def gambit(theme: str, w: float) -> str:
    c = THEMES[theme]
    n = len(STEPS)
    gap = 36 if w >= 600 else 16
    bw = (w - 4 - gap * (n - 1)) / n
    bh = 34
    y = 2
    parts: list[str] = []

    def left(i: int) -> float:
        return 2 + i * (bw + gap)

    for i, (label, human) in enumerate(STEPS):
        bx = left(i)
        stroke = c["accent"] if human else c["line"]
        parts.append(f'<rect x="{bx:.1f}" y="{y}" width="{bw:.1f}" height="{bh}" rx="{bh / 2}" fill="{c["node"]}" stroke="{stroke}" stroke-width="{1.5 if human else 1}"/>')
        parts.append(f'<text x="{bx + bw / 2:.1f}" y="{y + 22}" fill="{c["fg"]}" font-weight="600" text-anchor="middle">{label}</text>')
        if i < n - 1:
            ax0, ax1 = bx + bw + gap * 0.22, bx + bw + gap * 0.78
            ay = y + bh / 2
            parts.append(f'<line x1="{ax0:.1f}" y1="{ay}" x2="{ax1:.1f}" y2="{ay}" stroke="{c["muted"]}" stroke-width="1.5" stroke-linecap="round"/>')
            parts.append(f'<path d="M{ax1 - 4:.1f},{ay - 3.5} L{ax1:.1f},{ay} L{ax1 - 4:.1f},{ay + 3.5}" fill="none" stroke="{c["muted"]}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
    by = y + bh + 10
    for i in (0, n - 1):
        parts.append(f'<text x="{left(i) + bw / 2:.1f}" y="{by + 14}" fill="{c["accent"]}" font-size="12" text-anchor="middle">you</text>')
    a0, a1 = left(1) + 8, left(3) + bw - 8
    parts.append(f'<path d="M{a0:.1f},{by} V{by + 5} H{a1:.1f} V{by}" fill="none" stroke="{c["line"]}"/>')
    parts.append(f'<text x="{(a0 + a1) / 2:.1f}" y="{by + 20}" fill="{c["muted"]}" font-size="12" text-anchor="middle">agents, no check-ins</text>')
    return svg(w, by + 30, "".join(parts), "Gambit loop: contract, build, review, release, report")


for theme in THEMES:
    for suffix, w in SIZES.items():
        _ = (OUT / f"timeline{suffix}-{theme}.svg").write_text(timeline(theme, w))
        _ = (OUT / f"gambit{suffix}-{theme}.svg").write_text(gambit(theme, w))
