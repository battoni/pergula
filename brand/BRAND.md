# pergula — mark specification v1

The geometry, colour and limits of the mark, at the precision needed to rebuild
it from nothing. Where this disagrees with [`concept.md`](concept.md), the
concept wins. Where it disagrees with the `:root` block in `pergula`, the CSS
wins on colour.

## The mark

`pergula-icon.svg` — **a paragraph with a line snapped in two, the tail fallen
below.**

That sentence is the whole mark. It is a picture of **a quebra**, the first idea
in [`concept.md`](concept.md): the newline the terminal puts inside a paragraph,
invisible on screen and fatal on paste. **It is the enemy the product was built
against, drawn.**

Three lines of prose. The first is whole. The second stops mid-measure at a
diagonal shear. The third is the remainder, fallen a line and pushed right, its
leading edge the exact complement of the cut above — so the two halves visibly
reassemble.

## Geometry

Canvas 512 × 512. Every coordinate is a multiple of 32, so at 16px — where the
canvas divides by exactly 32 — every horizontal edge lands on a whole pixel and
only the shear is soft.

```
line 1  M32 32   L480 32  L480 128 L32 128  Z
line 2  M32 192  L288 192 L352 288 L32 288  Z
line 3  M288 352 L480 352 L480 448 L352 448 Z
```

| Measure | Value |
| --- | --- |
| Ink box | x 32–480, y 32–448 — **448 × 416** |
| Line thickness | 96 units — **exactly 3 real pixels at 16px** |
| Line gap | 64 units — 2 pixels |
| The shear | from (288, 192) to (352, 288): 64 across, 96 down |
| Padding | 32 left, 32 right, 32 top, **64 bottom** |

**The bottom padding is 64, not 32.** The mark sits high in its box because the
fallen tail already carries weight low and right. Tiles and avatars in `assets/`
correct for this and centre the ink; do not inherit the raw offset when placing
the mark inside a shape.

## Why these numbers

**Three lines, not four.** Four lines at 64 units gave 2-pixel bars at favicon
size and the break greyed out. Three lines at 96 units give **3 pixels**, and
that one pixel is the difference between a fracture you can see and a smudge.
Two lines cannot work: the break itself consumes two rows.

**A shear, not a chevron.** The first version ended line 2 in a V and began line
3 with the matching point. It read as an **arrow** or a play triangle — the
single most damaging misreading available, because an arrow means "next" and says
nothing about a break. The diagonal shear keeps the interlock and cannot be
mistaken for a pointer.

**Everything on the 32-unit module.** Six of twelve marks in an earlier round
blurred at 16px purely because their coordinates missed pixel boundaries.

## Colour

| Use | Value | Contrast |
| --- | --- | --- |
| Dark grounds (`#14120f`, `#141413`) | `#c0e021` | 12.40 : 1 |
| Light grounds | `#6d8214` | 4.33 : 1 |
| Knockout | mark in `#141413` on `#c0e021` | 12.22 : 1 |

One flat fill, always. Never a gradient, a second tone, a stroke, a shadow or a
glow. `#c0e021` measures 1.51 : 1 on white and must never be placed there.

**The lime is confirmed**, 5 September 2026, against 33 proofs in six sets —
see [`color/`](color/) and the finding in [`tokens.md`](tokens.md). In short: no
hue in the sweep beats it on contrast, so it wins by elimination rather than by
merit — its warm neighbours are Claude's coral family, its cool neighbours are
the vetoed neon. `#6d8214` is not a preference but the lightest ramp step that
clears 3:1 on white while still reading as lime.

## Scale

| Size | Behaviour |
| --- | --- |
| 16px | Minimum. Bars land on whole pixels; only the shear anti-aliases |
| 20px | In-app header, beside the session title |
| 32–64px | Favicon at higher density |
| 180–512px | OS tiles and avatars, ink re-centred |

One drawing at every size. There is no simplified small variant.

## The lockup

`pergula-lockup.svg` — 1744 × 512, mark left, wordmark right.

- **Space Grotesk SemiBold**, outlined to paths, so the file carries no font
  dependency onto a stranger's README.
- Type size 300 units on a 1000-unit em.
- Gap: 128 units.
- The word's ink block is optically centred against the mark's. There is no
  shared baseline to match — the mark is a paragraph, not a letter — so the fit
  was chosen by looking, at 260, 300 and 340, and 300 balanced.

**The symbol leads.** Never set the word larger than the mark's ink height.

## Clear space and limits

- **Clear space:** 64 units on all four sides of the ink box, scaling
  proportionally.
- **The tile is for OS icons only** — `assets/tile.svg` and everything generated
  from it. It must never appear as a container inside the logo.
- **One official knockout:** `assets/pergula-knockout.svg`.

## Never

Rotate it · recolour it outside the two brand values · stretch it · outline it ·
add a stroke, shadow, bevel or glow · put it in a rounded-square container · draw
it in perspective · redraw it off the 32-unit module · reduce the lines below 96
units · replace the shear with a chevron, a V or an arrow · add a fourth line.
