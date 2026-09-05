# pergula — mark specification v1

The geometry, colour and limits of the mark, at the precision needed to rebuild
it from nothing. Where this file disagrees with [SURVEY.md](SURVEY.md), the
survey wins. Where it disagrees with the theme block in `pergula`, the code wins
on colour.

## The mark

`pergula-icon.svg` — a lowercase p built as a structure: **a roof plate
projecting past the post that carries it, and the space it shelters.**

That sentence is the whole logic. If a future variant cannot be described by it,
it is not this mark.

## Geometry

Canvas 512 × 512. **The module is 32 units.** Every coordinate is a multiple of
32, with no exceptions — at 16px one module is exactly one real pixel, so the
mark rasterises with zero anti-aliasing.

| Member | x | y | w | h |
| --- | --- | --- | --- | --- |
| Roof plate | 96 | 32 | 320 | 64 |
| Right post | 352 | 96 | 64 | 96 |
| Bowl floor | 160 | 192 | 256 | 64 |
| Stem | 160 | 32 | 64 | 448 |

**Derived measures.**

- Ink box: x 96–416, y 32–480. **320 × 448**, centred, 96 units of padding left
  and right, 32 top and bottom.
- Every member is exactly 64 units — 2 modules — thick. Nothing is thicker or
  thinner.
- **Bowl** y 32–256 = 224 units. **Descender** y 256–480 = 224 units. Exactly
  equal, and that equality is what makes it read lowercase rather than as a
  capital P.
- **Counter** x 224–352, y 96–192 = 128 × 96. At 16px this is a clean 4 × 3 pixel
  void.
- **The step** is the roof plate's left edge at x 96 against the stem's at x 160:
  a **2-module overhang**, 64 units, the only offset in the outer silhouette.

## Why these numbers

**The descender equals the bowl.** In a typographic lowercase p the ratio is
about 2.4 : 1. Here it is 1 : 1, deliberately — round one of the exploration
produced twelve marks and *every legible one read as a capital P*, because the
bowl took 60–70% of the height. Equality is the correction, and it is not
negotiable.

**The module is 32.** Round one lost six of twelve marks to blur at 16px, purely
because coordinates did not land on pixel boundaries. Anything off the module
reintroduces that failure.

**The step, not the lap.** The survey specified a lapped joint as the craft
signature. It cannot exist in a single flat colour — two same-coloured members
that overlap merge. The overhang at the top-left is the surviving expression, and
it carries more meaning than the lap did: it is the roof projecting past its
post, which is the product's name.

## Colour

| Use | Value | Contrast |
| --- | --- | --- |
| On dark grounds (`#14120f`, `#141413`) | `#c0e021` | 12.40 : 1 |
| On light grounds (white and near-white) | `#6d8214` | 4.33 : 1 |
| Knockout ground | `#c0e021` with the mark in `#141413` | 12.22 : 1 |

One flat fill, always. **Never** a gradient, a second tone, a stroke, a shadow,
or a glow. `#c0e021` measures 1.51 : 1 on white and must never be placed there.

## Scale

| Size | Behaviour |
| --- | --- |
| 16px | Minimum. Verified in real pixels: 10 × 14, counter a clean 4 × 3 void, zero anti-aliasing |
| 20px | In-app header, beside the session title |
| 32–64px | Favicon at higher density, tab icons |
| 180–512px | OS tiles, avatars |

The mark has **one** drawing at every size. There is no simplified small variant,
and there must never be one.

## The lockup

`pergula-lockup.svg` — 1839 × 512. Mark left, wordmark right, sharing a baseline.

- Wordmark: **Space Grotesk SemiBold**, outlined to paths, so the file carries no
  font dependency.
- Type size 330 units on a 1000-unit em.
- Gap between mark and word: **112 units**, 3.5 modules.
- The word's ink block is optically centred against the mark's, not
  metric-matched — matching x-heights or total ink makes one element tower over
  the other, because the mark's 1 : 1 bowl-to-descender is not a typographic
  ratio.

**The symbol leads.** In any lockup the mark reads first and the word labels it.
Never set the word larger than the mark's ink height.

## Clear space and limits

- **Clear space:** 64 units — 2 modules — on all four sides of the ink box,
  scaling proportionally.
- **The tile is permitted for OS-level icons only** (apple-touch, PWA, avatar):
  the mark at 62% of the tile on `#141413`. It must never appear as a container
  inside the logo itself.
- **One official knockout:** `assets/pergula-knockout.svg`. Nothing else reversed.

## Never

Rotate it · recolour it outside the two brand values · stretch it · outline it ·
add a stroke, shadow, bevel or glow · place it in a rounded-square container ·
set it in perspective · add foliage, vines or sunbeams · redraw it off the
32-unit module · reduce the descender below the bowl height.
