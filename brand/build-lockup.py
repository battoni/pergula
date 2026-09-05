#!/usr/bin/env python3
"""Rebuild pergula-lockup.svg from pergula-icon.svg and Space Grotesk.

The wordmark ships as outlines, not as <text>: a wordmark that depends on an
installed font renders wrong on a stranger's README.

The word is fitted optically rather than by a metric rule. There is no shared
baseline to match — the mark is a paragraph, not a letter — so 260, 300 and 340
were drawn and compared, and 300 balanced. Pass a different em to re-test.

  python3 build-lockup.py [em]
"""

import re
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONT = Path.home() / "Library/Fonts/SpaceGrotesk-SemiBold.ttf"

# Measured off pergula-icon.svg. The ink is 448 x 416 and sits 32 from the top,
# 64 from the bottom — deliberate, because the fallen tail already weighs low.
MARK_TOP, MARK_BOTTOM, MARK_RIGHT = 32, 448, 480
MARK_INK = MARK_BOTTOM - MARK_TOP
GAP = 128          # between mark and word
PAD = 32           # right padding, matching the mark's left


def outline(em: float) -> tuple[str, float, float]:
    font = TTFont(FONT)
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    scale = em / 1000

    top = bottom = None
    ink_right = advance = 0.0
    for ch in "pergula":
        name = cmap[ord(ch)]
        bounds = BoundsPen(gs)
        gs[name].draw(bounds)
        if bounds.bounds:
            _, y0, x1, y1 = bounds.bounds
            top = y1 if top is None else max(top, y1)
            bottom = y0 if bottom is None else min(bottom, y0)
            ink_right = max(ink_right, advance + x1)
        advance += hmtx[name][0]

    # Centre the word's ink block against the mark's.
    baseline = MARK_TOP + (MARK_INK - (top - bottom) * scale) / 2 + top * scale

    glyphs, pen_x = [], 0.0
    for ch in "pergula":
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(pen)
        if (d := pen.getCommands()):
            glyphs.append(f'<path d="{d}" transform="translate({pen_x:.0f} 0)"/>')
        pen_x += hmtx[name][0]

    left = MARK_RIGHT + GAP
    group = (f'<g id="wordmark" fill="#c0e021" transform="translate({left} '
             f'{baseline:.1f}) scale({scale:.6f} -{scale:.6f})">\n      '
             + "\n      ".join(glyphs) + "\n    </g>")
    return group, left + ink_right * scale, scale


def main() -> None:
    em = float(sys.argv[1]) if len(sys.argv) > 1 else 300
    word, right, scale = outline(em)
    shapes = "\n    ".join(
        re.findall(r"<path[^>]*/>", (HERE / "pergula-icon.svg").read_text()))
    width = round(right + PAD)

    out = HERE / "pergula-lockup.svg"
    out.write_text(
        f'<svg viewBox="0 0 {width} 512" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="pergula">\n  <g id="icon">\n    {shapes}\n  </g>\n'
        f'  {word}\n</svg>\n')
    print(f"{out.name}: {width}x512 (em {em:.0f}, scale {scale:.4f})")


if __name__ == "__main__":
    main()
