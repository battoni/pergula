#!/usr/bin/env python3
"""Contact sheet for the pergula marks: every icon on the app ground and on white.

The light version is not the same file recoloured by CSS — it is the real
#6d8214 the brand spec calls for, substituted into the markup, because that is
what will actually ship.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIME, OLIVE = "#c0e021", "#6d8214"
PATTERN = sys.argv[1] if len(sys.argv) > 1 else "mark-*-icon.svg"

CARD = """  <div class="card">
    <div class="pair">
      <div class="on-dark">{dark}</div>
      <div class="on-light">{light}</div>
    </div>
    <div class="label">{name}</div>
  </div>"""

PAGE = """<!doctype html><meta charset="utf-8">
<title>pergula — marcas</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font:14px/1.5 "Space Grotesk", -apple-system, sans-serif;
         padding:2rem; background:#141413; color:#d1d1ce; }}
  h1 {{ font-size:1.35rem; margin-bottom:.3rem; color:#f5f5f4; }}
  .lede {{ color:#7a7a76; font-size:.88rem; margin-bottom:1.8rem; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:1.1rem; }}
  .card {{ border:1px solid #2a2a28; border-radius:2px; overflow:hidden; }}
  .pair {{ display:grid; grid-template-columns:1fr 1fr; }}
  .on-dark, .on-light {{ display:flex; align-items:center; justify-content:center;
                        padding:1.4rem; min-height:150px; }}
  .on-dark {{ background:#14120f; }}
  .on-light {{ background:#ffffff; border-left:1px solid #2a2a28; }}
  .pair svg {{ width:104px; height:104px; display:block; }}
  .label {{ padding:.55rem .8rem; font-size:.8rem; font-weight:500;
           border-top:1px solid #2a2a28; background:#1f1f1e; color:#c0e021; }}
</style>
<h1>pergula — fase 3</h1>
<p class="lede">Every mark on the app ground (#14120f) and on white, in the
colour that actually ships on each: {lime} and {olive}.</p>
<div class="grid">
{cards}
</div>"""


def inline(path: Path, colour: str) -> str:
    svg = path.read_text()
    svg = re.sub(r'#[cC]0[eE]021', colour, svg)
    return re.sub(r"<\?xml.*?\?>", "", svg, flags=re.S).strip()


def main() -> None:
    icons = sorted(HERE.glob(PATTERN))
    if not icons:
        sys.exit("no marks in " + str(HERE))
    cards = "\n".join(
        CARD.format(name=p.stem.replace("-icon", ""),
                    dark=inline(p, LIME), light=inline(p, OLIVE))
        for p in icons
    )
    out = HERE / "contact-sheet.html"
    out.write_text(PAGE.format(cards=cards, lime=LIME, olive=OLIVE))
    print(f"{out}: {len(icons)} marks")


if __name__ == "__main__":
    main()
