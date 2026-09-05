#!/usr/bin/env python3
"""Six sets of colour proofs for the pergula mark.

Confirmation by comparison, not by inheritance. Each swatch carries its measured
contrast against the ground it sits on, so the sheet can be argued with.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab import contrast, to_lch, from_lch

HERE = Path(__file__).resolve().parent
MARK = re.findall(r"<path[^>]*d=\"([^\"]+)\"", (HERE.parent / "pergula-icon.svg").read_text())
DARK, LIGHT = "#14120f", "#ffffff"

RAMP = [("300", "#d4ef5a"), ("400", "#c8e83a"), ("500", "#c0e021"),
        ("600", "#a8c41c"), ("700", "#8aa318"), ("800", "#6d8214"), ("900", "#4f6010")]

L0, C0, H0 = to_lch("#c0e021")
HUES = [(f"{h}°", from_lch(L0, C0, h)) for h in (60, 80, 100, 120, 140, 160, 180)]

OTHERS = [("terracota antiga", "#d98b63"), ("coral Claude", "#d97757"),
          ("light ink", "#f2ece4"), ("white", "#ffffff"),
          ("amber", "#e0b35c"), ("paper green", "#85b06b")]


def mark(fill: str, size: int) -> str:
    paths = "".join(f'<path d="{d}" fill="{fill}"/>' for d in MARK)
    return (f'<svg viewBox="0 0 512 512" width="{size}" height="{size}" '
            f'style="display:block">{paths}</svg>')


def swatch(label: str, colour: str, ground: str, size: int = 76) -> str:
    ratio = contrast(colour, ground)
    flag = "" if ratio >= 3 else " low"
    return (f'<div class="s{flag}"><div class="w" style="background:{ground}">'
            f'{mark(colour, size)}</div>'
            f'<div class="m"><b>{label}</b><span>{colour}</span>'
            f'<em>{ratio:.2f}</em></div></div>')


def block(title: str, note: str, rows: str) -> str:
    return f'<h2>{title}</h2><p class="n">{note}</p><div class="row">{rows}</div>'


def build_pixel_rasters() -> None:
    """The 16px strip needs real rasters, not scaled images. These were once made
    by hand, which meant the sheet could not be rebuilt from the script alone."""
    px = HERE / "px"
    px.mkdir(exist_ok=True)

    for name, colour in (("500", "#c0e021"), ("400", "#c8e83a"), ("600", "#a8c41c")):
        body = "".join(f'<path d="{d}" fill="{colour}"/>' for d in MARK)
        source = px / f".{name}.svg"
        source.write_text(f'<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">{body}</svg>')

        for index in (0, 1):
            subprocess.run(["rsvg-convert", "-w", "16", "-h", "16", str(source),
                            "-o", str(px / f"{name}-{index}.png")], check=True)

        source.unlink()


def main() -> None:
    build_pixel_rasters()
    parts = []

    parts.append(block(
        "1 — the Battoni Dev ramp on the app ground",
        f"Which step is actually right on {DARK}? Inheritance says 500.",
        "".join(swatch(n, c, DARK) for n, c in RAMP)))

    parts.append(block(
        "2 — the same ramp on white",
        "The light value must clear 3:1 for graphics. Red = fails.",
        "".join(swatch(n, c, LIGHT) for n, c in RAMP)))

    parts.append(block(
        "3 — hue rotation, L and C held constant",
        f"All at L={L0:.3f} C={C0:.3f}; only the hue moves. 120 is the current lime. "
        "If a neighbour looks just as good, the lime is not winning on merit.",
        "".join(swatch(n, c, DARK) for n, c in HUES)))

    parts.append(block(
        "4 — what if it is not green",
        "Sanity check: is the colour doing work, or would any light value do?",
        "".join(swatch(n, c, DARK) for n, c in OTHERS)))

    finals = [("500 lima", "#c0e021"), ("400", "#c8e83a"), ("600", "#a8c41c")]
    parts.append(block(
        "5 — at 16px, real favicon size",
        "Magnified with nearest-neighbour. This is the pixel that reaches the tab.",
        "".join(f'<div class="s"><div class="w" style="background:{g}">'
                f'<img src="px/{n.split()[0]}-{i}.png" width="64" '
                f'style="image-rendering:pixelated;display:block">'
                f'</div><div class="m"><b>{n}</b><span>{c}</span></div></div>'
                for n, c in finals for i, g in enumerate((DARK, LIGHT)))))

    Path(HERE / "proofs.html").write_text(f"""<!doctype html><meta charset=utf-8>
<style>*{{margin:0;padding:0;box-sizing:border-box}}
body{{font:13px "Space Grotesk",-apple-system,sans-serif;padding:28px;background:#1f1f1e;color:#d1d1ce}}
h1{{font-size:1.35rem;color:#f5f5f4}} h2{{font-size:1rem;color:#f5f5f4;margin:2rem 0 .2rem}}
p.n,p.l{{color:#7a7a76;font-size:.84rem;margin-bottom:.9rem;max-width:70ch}}
.row{{display:flex;flex-wrap:wrap;gap:10px}}
.s{{border:1px solid #3d3d3a;width:126px}}
.s.low{{border-color:#8a3a2a}}
.w{{padding:14px;display:flex;align-items:center;justify-content:center;min-height:104px}}
.m{{padding:6px 8px;background:#141413;border-top:1px solid #3d3d3a;font-size:.74rem;line-height:1.5}}
.m b{{display:block;color:#c0e021}} .m span{{display:block;color:#7a7a76;font-family:ui-monospace,monospace}}
.m em{{display:block;font-style:normal;color:#d1d1ce}}
.s.low .m em{{color:#e0705a}}
</style>
<h1>pergula — colour proofs</h1>
<p class="l">Confirmation by comparison, not by inheritance. The number on each
swatch is its measured contrast against the ground it sits on.</p>
{''.join(parts)}""")
    print("proofs.html")


if __name__ == "__main__":
    main()
