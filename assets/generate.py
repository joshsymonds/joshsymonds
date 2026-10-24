# /// script
# dependencies = ["fonttools"]
# ///
"""Generate the README's Memphis graphics, echoing joshsymonds.com.

Text is outlined from Space Grotesk so it renders the same everywhere:

    curl -L -o /tmp/SpaceGrotesk.ttf 'https://github.com/google/fonts/raw/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf'
    uv run assets/generate.py /tmp/SpaceGrotesk.ttf
"""

import math
import sys
from pathlib import Path
from typing import final

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

OUT = Path(__file__).parent

TEAL, CORAL, YELLOW, PINK = "#2ec4b6", "#ff6b6b", "#ffd166", "#ffb6c1"
INK, CREAM = "#1a1a1a", "#f4f0e6"
PAGE, PAGE_DARK = "#ffffff", "#0d1117"

# Outlines and shadows flip to cream in dark mode, as the site's --black does.
# .h is a halo in GitHub's page color that separates a letter from what sits behind it.
STYLE = (
    f"<style>.i{{fill:{INK}}}.s{{stroke:{INK}}}.h{{stroke:{PAGE}}}"
    f"@media (prefers-color-scheme:dark){{.i{{fill:{CREAM}}}.s{{stroke:{CREAM}}}.h{{stroke:{PAGE_DARK}}}}}</style>"
)


@final
class Face:
    def __init__(self, path: str, weight: int) -> None:
        font = instantiateVariableFont(TTFont(path), {"wght": weight})
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm

    def advance(self, ch: str, size: float) -> float:
        return self.glyphs[self.cmap[ord(ch)]].width * size / self.upm

    def width(self, text: str, size: float) -> float:
        return sum(self.advance(ch, size) for ch in text)

    def path(self, text: str, size: float, x: float, y: float) -> str:
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs)
        for ch in text:
            name = self.cmap[ord(ch)]
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
            x += self.glyphs[name].width * scale
        return pen.getCommands()


def svg(w: float, h: float, body: str, label: str) -> str:
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.1f} {h:.1f}" {aria}>{STYLE}{body}</svg>\n'
    )


def wave(x0: float, y: float, length: float, amp: float, step: float) -> str:
    d = f"M{x0:.1f},{y:.1f}"
    x, up = x0, True
    while x + step <= x0 + length:
        d += f" Q{x + step / 2:.1f},{y - amp if up else y + amp:.1f} {x + step:.1f},{y:.1f}"
        x += step
        up = not up
    return d


def wordmark(bold: Face) -> str:
    size, border = 40.0, 2.5
    base = size * 0.95
    mark = size * 0.55
    parts: list[str] = []
    x = border

    def letters(text: str, halo: bool = False) -> None:
        nonlocal x
        outline = ' stroke-width="4" stroke-linejoin="round" paint-order="stroke"' if halo else ""
        parts.append(f'<path class="i{" h" if halo else ""}"{outline} d="{bold.path(text, size, x, base)}"/>')
        x += bold.width(text, size)

    def o_shape(kind: str) -> None:
        nonlocal x
        adv = bold.advance("o", size)
        cx = x + adv / 2
        if kind == "circle":
            r = mark / 2 - border / 2
            parts.append(f'<circle cx="{cx:.1f}" cy="{base - mark / 2:.1f}" r="{r:.1f}" fill="{TEAL}" class="s" stroke-width="{border}"/>')
        else:
            s = mark - border
            parts.append(f'<rect x="{cx - s / 2:.1f}" y="{base - mark + border / 2:.1f}" width="{s:.1f}" height="{s:.1f}" fill="{PINK}" class="s" stroke-width="{border}"/>')
        x += adv

    josh = x
    letters("J")
    o_shape("circle")
    letters("sh")
    squiggle = wave(josh + size * 0.75, base - size * 0.8, size * 1.15, size * 0.06, size * 0.075)
    parts.append(f'<path d="{squiggle}" fill="none" class="s" stroke-width="1" stroke-linecap="round"/>')
    x += size * 0.3
    # A slanted yellow block behind the S, echoing the site's stripe without crossing the letter.
    bw, bh = bold.advance("S", size) + size * 0.16, size * 0.92
    top = base - size * 0.8
    lean = math.tan(math.radians(12)) * (top + bh / 2)
    block = f'x="{x - size * 0.08:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}"'
    parts.append(f'<rect {block} fill="{YELLOW}" class="s" stroke-width="{border}" transform="skewX(-12) translate({lean:.1f} 0)"/>')
    letters("S", halo=True)
    letters("ym")
    o_shape("square")
    letters("nds")
    return svg(x + border, size * 1.35, "".join(parts), "Josh Symonds")


STATS = [
    ("stat-years", "15 yrs", ("infrastructure", "and security"), TEAL),
    ("stat-m1", "#8", ("employee at", "M1 Finance"), YELLOW),
    ("stat-dynamoid", "13M+", ("Dynamoid", "downloads"), CORAL),
    ("stat-nix", "800+", ("stars on", "nix-config"), PINK),
    ("stat-savecraft", "14", ("games in", "Savecraft"), TEAL),
    ("stat-edge", "123", ("edge sites", "shipped"), YELLOW),
]


def tile(bold: Face, medium: Face, big: str, lines: tuple[str, str], color: str) -> str:
    w, h, border, shadow = 124.0, 84.0, 2.5, 4.0
    o = border / 2
    parts = [
        f'<rect x="{o + shadow:.1f}" y="{o + shadow:.1f}" width="{w - border:.1f}" height="{h - border:.1f}" rx="4" class="i"/>',
        f'<rect x="{o:.1f}" y="{o:.1f}" width="{w - border:.1f}" height="{h - border:.1f}" rx="4" fill="{color}" stroke="{INK}" stroke-width="{border}"/>',
        f'<path fill="{INK}" d="{bold.path(big, 28, 12, 38)}"/>',
        f'<path fill="{INK}" d="{medium.path(lines[0], 12, 12, 58)}"/>',
        f'<path fill="{INK}" d="{medium.path(lines[1], 12, 12, 72)}"/>',
    ]
    return svg(w + shadow, h + shadow, "".join(parts), f"{big} {lines[0]} {lines[1]}")


def glyph(kind: str) -> str:
    sw = 2.5
    cls = f'class="s" stroke-width="{sw}" stroke-linejoin="round"'
    if kind == "savecraft":  # floppy disk
        body = (
            f'<path d="M4,3 H24 L29,8 V29 H4 Z" fill="{CORAL}" {cls}/>'
            f'<rect x="9" y="3" width="12" height="8" fill="{CREAM}" {cls}/>'
            f'<rect x="16" y="5" width="3" height="4" class="i"/>'
            f'<rect x="8" y="17" width="17" height="12" fill="{CREAM}" {cls}/>'
        )
    elif kind == "gambit":  # pawn
        body = (
            f'<path d="M11,16 H21 L23,25 H9 Z" fill="{YELLOW}" {cls}/>'
            f'<rect x="6" y="25" width="20" height="5" rx="1" fill="{YELLOW}" {cls}/>'
            f'<rect x="10" y="13" width="12" height="3.5" rx="1" fill="{YELLOW}" {cls}/>'
            f'<circle cx="16" cy="8" r="5.5" fill="{YELLOW}" {cls}/>'
        )
    elif kind == "nix":  # snowflake
        arms = "".join(
            f'<line x1="16" y1="16" x2="{16 + 12 * math.cos(math.radians(a)):.1f}" y2="{16 + 12 * math.sin(math.radians(a)):.1f}"/>'
            for a in range(30, 390, 60)
        )
        body = (
            f'<g class="s" stroke-width="6.5" stroke-linecap="round">{arms}</g>'
            f'<g stroke="{TEAL}" stroke-width="2.5" stroke-linecap="round">{arms}</g>'
        )
    else:  # dynamoid: database cylinder
        body = (
            f'<path d="M5,8 V24 A11,4 0 0 0 27,24 V8" fill="{PINK}" {cls}/>'
            f'<path d="M5,16 A11,4 0 0 0 27,16" fill="none" {cls}/>'
            f'<ellipse cx="16" cy="8" rx="11" ry="4" fill="{PINK}" {cls}/>'
        )
    return svg(32, 32, body, "")


def shape(kind: str) -> str:
    sw = 2.5
    if kind == "circle":
        body = f'<circle cx="12" cy="12" r="9.5" fill="{TEAL}" class="s" stroke-width="{sw}"/>'
    elif kind == "triangle":
        body = f'<path d="M12,3 L22,21 H2 Z" fill="{CORAL}"/>'
    elif kind == "diamond":
        body = f'<rect x="5.5" y="5.5" width="13" height="13" fill="{YELLOW}" class="s" stroke-width="{sw}" transform="rotate(45 12 12)"/>'
    elif kind == "square":
        body = f'<rect x="4" y="4" width="16" height="16" fill="{PINK}" class="s" stroke-width="{sw}"/>'
    else:  # squiggle
        body = f'<path d="{wave(2, 12, 20, 5, 5)}" fill="none" class="s" stroke-width="2.5" stroke-linecap="round"/>'
    return svg(24, 24, body, "")


def main() -> None:
    bold, medium = Face(sys.argv[1], 700), Face(sys.argv[1], 500)
    files = {"wordmark.svg": wordmark(bold)}
    for name, big, lines, color in STATS:
        files[f"{name}.svg"] = tile(bold, medium, big, lines, color)
    for kind in ("savecraft", "gambit", "nix", "dynamoid"):
        files[f"glyph-{kind}.svg"] = glyph(kind)
    for kind in ("circle", "triangle", "diamond", "square", "squiggle"):
        files[f"shape-{kind}.svg"] = shape(kind)
    for name, content in files.items():
        _ = (OUT / name).write_text(content)


if __name__ == "__main__":
    main()
