# Colour proofs

Run 5 September 2026, to confirm `#c0e021` **by comparison rather than by
inheritance** — the standard lifeshifter set in its rodada 9.

`lab.py` does the colour maths. Hue rotation is in **OKLCh, not HSL**: rotating
hue in HSL changes perceived lightness wildly, so an HSL "same colour, different
hue" comparison is not comparing what it claims to. `proofs.py` builds the sheet;
`proofs.png` is the result.

`#c0e021` is **L 0.854, C 0.195, H 119.8°** in OKLCh.

## What the six sets found

**1 — the ramp on `#14120f`.** Every step from 300 to 800 clears contrast; only
900 fails, at 2.68. The dark ground does not constrain the choice at all.

**2 — the ramp on white.** Steps 300 (1.29), 400 (1.39), 500 (1.51), 600 (1.99)
and 700 (2.86) **all fail** the 3:1 threshold for graphics. Only 800 (4.33) and
900 (6.97) pass. `#6d8214` is therefore the lightest usable step that still reads
as lime — a measured constraint, not a preference.

**3 — hue rotation at constant L and C.** 60° 9.88 · 80° 11.16 · 100° 12.16 ·
**120° (lime) 12.38** · 140° 12.72 · 160° 12.87 · 180° 13.47. Contrast rises
monotonically toward cyan. **There is no technical case for lime.** It survives
because its neighbours are ruled out on brand grounds: warm lands in Claude's
coral family, cool lands in the neon-on-black sticker look the survey vetoed.

**4 — not green.** Ink `#f2ece4` 15.93, white 18.70, terracotta 6.97, Claude
coral 5.99. Monochrome outperforms every colour tested. **The lime is buying the
tie to Battoni Dev, not readability.**

**5 — 16px.** The finalists at real favicon size on both grounds, magnified with
nearest-neighbour.

## The verdict

**`#c0e021` confirmed, by elimination.** It wins no measurement; it is the only
hue that is neither adjacent to Claude nor neon, and it keeps exact parity with
the parent brand's primary-500.

**`#6d8214` confirmed, by measurement.** It is forced by set 2.

Re-run with `python3 color/proofs.py` after any change to `pergula-icon.svg` —
the proofs draw the real mark, not a swatch.
