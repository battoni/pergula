#!/usr/bin/env python3
"""Rebuild every application asset from pergula-icon.svg.

Nothing under assets/ is drawn by hand. Edit the icon, run this, and the favicon,
the tiles, the avatar and the README header all follow — which is the only way
the mark cannot drift between surfaces.

Needs rsvg-convert and ImageMagick, unlike the product itself.
"""

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"

LIME = "#c0e021"      # brand value, dark grounds
OLIVE = "#6d8214"     # the lightest ramp step that clears 3:1 on white
INK = "#141413"

# Measured off the icon: the ink is 448 x 416 and sits 32 from the top, 64 from
# the bottom. That offset is deliberate — the fallen tail already weighs low —
# so tiles re-centre rather than inherit it.
INK_X, INK_Y, INK_W, INK_H = 32, 32, 448, 416
TILE_RATIO = 0.66


def icon_shapes(fill=True):
    source = (HERE / "pergula-icon.svg").read_text()
    shapes = "\n    ".join(re.findall(r"<path[^>]*/>", source))
    if fill:
        return shapes

    return shapes.replace(f' fill="{LIME}"', "")


def svg(name, body):
    path = ASSETS / name
    path.write_text(body)
    return path


def raster(source, target, size):
    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size),
                    str(source), "-o", str(target)], check=True)


def build_favicon():
    """One file for both browser chromes: lime on dark, olive on light. The
    media query lives inside the SVG so there is no second asset to keep in sync."""
    return svg("favicon.svg",
               '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">\n'
               '  <style>\n'
               f'    #icon {{ fill: {OLIVE}; }}\n'
               f'    @media (prefers-color-scheme: dark) {{ #icon {{ fill: {LIME}; }} }}\n'
               '  </style>\n'
               f'  <g id="icon">\n    {icon_shapes(fill=False)}\n  </g>\n</svg>\n')


def build_tile():
    """Permitted for OS icons only, never as part of the logo."""
    scale = 512 * TILE_RATIO / INK_W
    x = (512 - INK_W * scale) / 2 - INK_X * scale
    y = (512 - INK_H * scale) / 2 - INK_Y * scale
    return svg("tile.svg",
               '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">'
               f'<rect width="512" height="512" fill="{INK}"/>'
               f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.4f})">'
               f'{icon_shapes()}</g></svg>')


def build_knockout():
    """The one official reversed form."""
    return svg("pergula-knockout.svg",
               '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">\n'
               f'  <rect width="512" height="512" fill="{LIME}"/>\n'
               f'  <g id="icon" fill="{INK}">\n    {icon_shapes(fill=False)}\n  </g>\n</svg>\n')


def build_card(name, width_px, ratio):
    """The lockup centred on ink, at 2:1. The README header and the GitHub
    social preview are the same composition at two sizes, so they share this
    rather than drifting apart."""
    height_px = width_px // 2
    lockup = (HERE / "pergula-lockup.svg").read_text()
    art_w = int(re.search(r'viewBox="0 0 (\d+)', lockup).group(1))
    inner = lockup.split(">", 1)[1].rsplit("</svg>", 1)[0].strip()

    scale = (width_px * ratio) / art_w
    source = HERE / ".card.svg"
    source.write_text(
        f'<svg viewBox="0 0 {width_px} {height_px}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="{width_px}" height="{height_px}" fill="{INK}"/>'
        f'<g transform="translate({(width_px - art_w * scale) / 2:.1f} '
        f'{(height_px - 512 * scale) / 2:.1f}) scale({scale:.4f})">{inner}</g></svg>')

    subprocess.run(["rsvg-convert", "-w", str(width_px), "-h", str(height_px),
                    str(source), "-o", str(ASSETS / name)], check=True)
    source.unlink()


def build_ico(favicon):
    """The ICO cannot carry a media query, so it takes the fixed value that
    clears 4.3:1 on both a light and a dark browser chrome."""
    flat = re.sub(r"<style>.*?</style>", "", favicon.read_text(), flags=re.S)
    source = HERE / ".ico.svg"
    source.write_text(flat.replace('<g id="icon">', f'<g id="icon" fill="{OLIVE}">'))

    sizes = []
    for size in (16, 32, 48):
        target = HERE / f".ico-{size}.png"
        raster(source, target, size)
        sizes.append(target)

    subprocess.run(["magick", *map(str, sizes), str(ASSETS / "favicon.ico")], check=True)
    for path in [source, *sizes]:
        path.unlink()


def main():
    if not (HERE / "pergula-icon.svg").exists():
        sys.exit("build-assets: pergula-icon.svg is missing")

    ASSETS.mkdir(exist_ok=True)

    favicon = build_favicon()
    tile = build_tile()
    build_knockout()

    for name, size in (("apple-touch-icon.png", 180), ("pwa-192.png", 192),
                       ("pwa-512.png", 512), ("avatar-512.png", 512)):
        raster(tile, ASSETS / name, size)

    build_card("readme-header.png", 1024, 0.74)
    build_card("social-preview.png", 1280, 0.62)
    build_ico(favicon)

    print(f"  {len(list(ASSETS.iterdir()))} assets rebuilt in {ASSETS}")


if __name__ == "__main__":
    main()
