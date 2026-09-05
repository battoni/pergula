#!/usr/bin/env python3
"""Round-two checks: the module, the lowercase proportion, the step.

Round one failed on three things a human eye caught only after rasterising.
All three are arithmetic, so they belong in a script from now on.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = 32          # one real pixel at 16px
MIN_MEMBER = 64      # two modules


def numbers(svg: str) -> list[float]:
    vals = [float(n) for n in re.findall(r'(?:x|y|width|height)="(-?\d+(?:\.\d+)?)"', svg)]
    for d in re.findall(r'\sd="([^"]+)"', svg):
        vals += [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", d)]
    return vals


def bounds(svg: str) -> tuple[float, float]:
    """Vertical extent of the ink, from rects and from path V/M commands."""
    ys = []
    for r in re.findall(r"<rect\b[^>]*>", svg):
        y = re.search(r'\sy="(-?\d+(?:\.\d+)?)"', r)
        h = re.search(r'\sheight="(-?\d+(?:\.\d+)?)"', r)
        if y and h:
            ys += [float(y.group(1)), float(y.group(1)) + float(h.group(1))]
    for d in re.findall(r'\sd="([^"]+)"', svg):
        tokens = re.findall(r"([MmHhVvLlZz])|(-?\d+(?:\.\d+)?)", d)
        cmd, pending = "", []
        for letter, num in tokens:
            if letter:
                cmd, pending = letter, []
                continue
            pending.append(float(num))
            moved = cmd in "MmLl" and len(pending) == 2
            if moved:
                ys.append(pending[1])
                pending = []
                continue

            vertical = cmd in "Vv" and len(pending) == 1
            if vertical:
                ys.append(pending[0])
                pending = []
                continue

            horizontal = cmd in "Hh" and len(pending) == 1
            if horizontal:
                pending = []
    return (min(ys), max(ys)) if ys else (0.0, 0.0)


def check(path: Path) -> list[str]:
    svg = path.read_text()
    bad = []

    offgrid = sorted({n for n in numbers(svg) if n % MODULE})
    if offgrid:
        bad.append(f"off the {MODULE}-unit module: {offgrid[:8]}")

    for r in re.findall(r"<rect\b[^>]*>", svg):
        for axis in ("width", "height"):
            m = re.search(rf'\s{axis}="(-?\d+(?:\.\d+)?)"', r)
            too_thin = m and float(m.group(1)) < MIN_MEMBER
            if too_thin:
                bad.append(f"member < {MIN_MEMBER}: {axis}={m.group(1)}")

    colours = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{3,8}", svg)}
    if colours != {"#c0e021"}:
        bad.append(f"colours: {sorted(colours) or 'none'}")
    if re.search(r"\b(stroke|opacity|transform|rx|ry)=", svg):
        bad.append("forbidden attribute")
    if re.search(r"[CcSsQqTtAa]", " ".join(re.findall(r'\sd="([^"]+)"', svg))):
        bad.append("curve in a path")

    top, bottom = bounds(svg)
    height = bottom - top
    if height:
        bad.append(f"INFO ink height: {top:.0f}–{bottom:.0f} ({height:.0f}u, "
                   f"{height / MODULE:.0f} modules)")

    return bad


def main() -> None:
    marks = sorted(HERE.glob("r2-*-icon.svg"))
    if not marks:
        sys.exit("no round-two marks yet")
    fails = 0
    for path in marks:
        issues = check(path)
        hard = [i for i in issues if not i.startswith("INFO")]
        info = [i for i in issues if i.startswith("INFO")]
        print(f"{'✗' if hard else '✓'} {path.stem}")
        for item in hard + info:
            print(f"    {item}")
        fails += bool(hard)
    print(f"\n{len(marks) - fails}/{len(marks)} passed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
