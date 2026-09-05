# pergula — image prompt and selection protocol

For generating exploratory marks with an image model or a code-writing agent, and
for turning the result into a shippable file. The mark shipped in v1 was produced
by the agent route below, not by an image model — that is recorded here because
it matters for reproducibility.

## The prompt

> A logo mark for "pergula", a local reader for developer terminal transcripts.
> A lowercase letter **p** built as an architectural structure: a horizontal roof
> plate projecting past the vertical post that carries it, with a rectangular
> void beneath read as the sheltered space. Entirely orthogonal — every corner a
> hard 90°, no rounded corners anywhere, no curves, no diagonals. One flat solid
> colour, acid lime `#c0e021`, on a near-black `#141413` ground. No gradient, no
> glow, no shadow, no outline, no container or tile around the mark. Constructed
> and engineered, like a steel bracket; not decorative, not organic, not
> illustrative. The descender below the bowl is exactly as deep as the bowl is
> tall, so it reads unmistakably as a lowercase p and never as a capital P. Flat
> vector, centred, generous margin.

## Variations worth trying

1. **Roof overhang** — the plate projects past the post at the top-left. *(This
   is the shipped mark.)*
2. **Offset plates** — two plates stepping in opposite directions, the parent
   brand's construction.
3. **Counter-dominant** — the void sized so it is the first thing registered.
4. **Stepped knockout** — the p cut out of a stepped field, escaping its bottom edge.
5. **Minimum members** — the fewest rectangles that can carry the letter.

## What image models get wrong here

Every one of these was observed in practice, so check for them first:

- **The capital P.** By far the most common failure. Models default to
  typographic proportions and the mark reads as a capital against a lowercase
  brand. Verify the descender is at least as deep as the bowl.
- **Sneaking in a radius.** Small corner rounding appears unbidden and reads as a
  different brand. It also disappears at 16px, so it is paid for and not received.
- **The tile.** Models love putting a mark inside a rounded square. Banned.
- **Depth.** Any shadow, bevel or gradient. Banned.
- **The garden centre.** The name pulls toward foliage, sunbeams, and pergolas in
  perspective. Banned.

## Selection protocol

1. **Lint before looking.** `marks/r2-lint.py` checks the module, member
   thickness, colour count, banned attributes and curves. A mark that fails is
   not worth an opinion.
2. **Rasterise for real.** `scripts/size-ladder.py` renders at 96, 32 and 16
   actual pixels and magnifies with nearest-neighbour. Never judge from
   `<img width="16">` — the browser's smooth resampling hides exactly the defect
   you are looking for.
3. **Both grounds.** `marks/contact-sheet.py` puts every mark on `#14120f` and on
   white, in the colour that actually ships on each — `#c0e021` and `#6d8214`,
   not one file recoloured by CSS.
4. **The eleven questions.** In [SURVEY.md](SURVEY.md). Any "no" sends it back.

## Vectorising a raster result

If a mark arrives as an image rather than as SVG, do not trace it. Trace produces
curves and off-grid coordinates, and both are disqualifying here. **Measure it
and rebuild it** as `<rect>` elements on the 32-unit module — the whole mark is
four rectangles, which takes less time than cleaning a trace.

## Reproducing the shipped mark

`pergula-icon.svg` is four rectangles. The exact coordinates are in
[BRAND.md](BRAND.md). Every application asset is generated from that one file by
the build steps recorded in [README.md](README.md) — nothing in `assets/` is
drawn by hand, so the mark cannot drift between surfaces.
