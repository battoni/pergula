#!/usr/bin/env python3
"""Check every mark against the phase-3 rules before it earns a raster test.

Cheap to run, and it catches the failures that are invisible in a preview:
a stray colour, a curve smuggled into a path, a member too thin to survive 16px.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_MEMBER = 56  # units; 16px divides the 512 canvas by 32, so 56 is 1.75 real px

BANNED_TAGS = ("circle", "ellipse", "defs", "style", "filter", "linearGradient",
               "radialGradient", "text", "image", "use")
BANNED_ATTRS = ("stroke", "opacity", "rx=", "ry=", "transform", "filter=")
CURVE_CMDS = re.compile(r"[CcSsQqTtAa]")


def check(path: Path) -> list[str]:
    svg = path.read_text()
    bad = []

    if 'viewBox="0 0 512 512"' not in svg:
        bad.append("viewBox is not 0 0 512 512")
    sized = re.search(r"<svg[^>]*\swidth=", svg) or re.search(r"<svg[^>]*\sheight=", svg)
    if sized:
        bad.append("svg tem width/height")

    groups = re.findall(r"<g\b[^>]*>", svg)
    wrong_group = len(groups) != 1 or 'id="icon"' not in groups[0]
    if wrong_group:
        bad.append(f"grupos: {len(groups)} (esperado 1 com id=icon)")

    colours = set(c.lower() for c in re.findall(r"#[0-9a-fA-F]{3,8}", svg))
    if colours != {"#c0e021"}:
        bad.append(f"colours: {sorted(colours) or 'none'}")

    for tag in BANNED_TAGS:
        if re.search(rf"<{tag}\b", svg):
            bad.append(f"tag proibida <{tag}>")
    for attr in BANNED_ATTRS:
        if attr in svg:
            bad.append(f"atributo proibido {attr.rstrip('=')}")

    for d in re.findall(r'\sd="([^"]+)"', svg):
        if CURVE_CMDS.search(d):
            bad.append("path contains a curve or arc")
            break

    # Full-canvas background rectangle?
    for r in re.findall(r"<rect\b[^>]*>", svg):
        w = re.search(r'width="(\d+)"', r)
        h = re.search(r'height="(\d+)"', r)
        full_canvas = w and h and int(w.group(1)) >= 512 and int(h.group(1)) >= 512
        if full_canvas:
            bad.append("background rectangle")

    # Thinnest rect dimension.
    thin = []
    for r in re.findall(r"<rect\b[^>]*>", svg):
        for axis in ("width", "height"):
            m = re.search(rf'{axis}="(\d+(?:\.\d+)?)"', r)
            too_thin = m and float(m.group(1)) < MIN_MEMBER
            if too_thin:
                thin.append(f"{axis}={m.group(1)}")
    if thin:
        bad.append(f"thin member: {', '.join(sorted(set(thin)))}")

    # Coordinates off the 8-unit grid.
    offgrid = {n for n in re.findall(r'(?:x|y|width|height)="(\d+(?:\.\d+)?)"', svg)
               if float(n) % 8}
    if offgrid:
        bad.append(f"off the 8-unit grid: {sorted(offgrid)[:6]}")

    return bad


def main() -> None:
    marks = sorted(HERE.glob("mark-*-icon.svg"))
    fails = 0
    for path in marks:
        bad = check(path)
        print(f"{'✗' if bad else '✓'} {path.stem}")
        for item in bad:
            print(f"    {item}")
        fails += bool(bad)
    print(f"\n{len(marks) - fails}/{len(marks)} passed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
