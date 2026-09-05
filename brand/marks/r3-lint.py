#!/usr/bin/env python3
"""Round-three checks. The rules changed, so the old linters no longer apply.

Diagonals are now legal — but only for the raked beam, and a diagonal's real
thickness is measured perpendicular to its run, not from its bounding box, which
is how a member that looks fine on screen turns out to be one pixel at 16px.
"""

import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_MEMBER = 56
GRID = 16
# The rafters mark was granted three parallel diagonals; everything else gets one.
DIAGONAL_BUDGET = {"r3-8-rafters-icon": 3}


def poly_points(raw: str) -> list[tuple[float, float]]:
    nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", raw)]
    return list(zip(nums[::2], nums[1::2]))


def strip_thickness(pts: list[tuple[float, float]]) -> float:
    """Perpendicular width of a 4-point parallelogram beam."""
    if len(pts) != 4:
        return math.inf
    best = math.inf
    for i in range(4):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % 4]
        cx, cy = pts[(i + 2) % 4]
        run = math.hypot(bx - ax, by - ay)
        if run < 1e-6:
            continue
        # distance from the next vertex to the line through a-b
        d = abs((bx - ax) * (ay - cy) - (ax - cx) * (by - ay)) / run
        best = min(best, d)
    return best


def check(path: Path) -> list[str]:
    svg = path.read_text()
    bad, info = [], []

    if 'viewBox="0 0 512 512"' not in svg:
        bad.append("viewBox is not 0 0 512 512")
    if re.search(r"<svg[^>]*\s(width|height)=", svg):
        bad.append("svg has width/height")

    groups = re.findall(r"<g\b[^>]*>", svg)
    wrong_group = len(groups) != 1 or 'id="icon"' not in groups[0]
    if wrong_group:
        bad.append(f"groups: {len(groups)} (expected 1 with id=icon)")

    colours = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{3,8}", svg)}
    if colours != {"#c0e021"}:
        bad.append(f"colours: {sorted(colours) or 'none'}")
    if re.search(r"\s(stroke|opacity|transform|rx|ry|filter)=", svg):
        bad.append("forbidden attribute")
    for tag in ("circle", "ellipse", "defs", "style", "text", "image", "use"):
        if re.search(rf"<{tag}\b", svg):
            bad.append(f"forbidden tag <{tag}>")
    if re.search(r"[CcSsQqTtAa]", " ".join(re.findall(r'\sd="([^"]+)"', svg))):
        bad.append("curve in a path")

    polys = re.findall(r'<polygon[^>]*points="([^"]+)"', svg)
    budget = DIAGONAL_BUDGET.get(path.stem, 1)
    if len(polys) > budget:
        bad.append(f"{len(polys)} diagonals (budget: {budget})")
    for raw in polys:
        t = strip_thickness(poly_points(raw))
        if t < MIN_MEMBER:
            bad.append(f"thin beam: {t:.0f}u perpendicular (min {MIN_MEMBER})")
            continue

        info.append(f"INFO diagonal beam: {t:.0f}u perpendicular")

    rects = re.findall(r"<rect\b[^>]*>", svg)
    for r in rects:
        w = re.search(r'\swidth="(\d+(?:\.\d+)?)"', r)
        h = re.search(r'\sheight="(\d+(?:\.\d+)?)"', r)
        if w and h:
            full_canvas = float(w.group(1)) >= 512 and float(h.group(1)) >= 512
            if full_canvas:
                bad.append("background rectangle")
            if min(float(w.group(1)), float(h.group(1))) < MIN_MEMBER:
                bad.append(f"thin member: {min(float(w.group(1)), float(h.group(1))):.0f}u")

    offgrid = sorted({n for n in re.findall(r'(?:x|y|width|height)="(\d+(?:\.\d+)?)"', svg)
                      if float(n) % GRID})
    if offgrid:
        bad.append(f"rect off the {GRID}-unit grid: {offgrid[:6]}")

    info.append(f"INFO {len(rects)} rects + {len(polys)} diagonals")
    return bad + info


def main() -> None:
    marks = sorted(HERE.glob("r3-*-icon.svg"))
    if not marks:
        sys.exit("no round-three marks yet")
    fails = 0
    for path in marks:
        issues = check(path)
        hard = [i for i in issues if not i.startswith("INFO")]
        print(f"{'✗' if hard else '✓'} {path.stem}")
        for item in issues:
            print(f"    {item}")
        fails += bool(hard)
    print(f"\n{len(marks) - fails}/{len(marks)} passed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
