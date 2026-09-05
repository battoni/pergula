# Direction — the decisions, and why

Every closed decision with its reason attached, so that a year from now the
reasoning is recoverable and a change can be argued with rather than guessed at.

This file exists because its absence cost this project two complete attempts.
The diagnosis that eventually unlocked it had been written down in
`lifeshifter/brand/DIRECAO-MARCA.md` two weeks earlier, and nobody read it.

---

## The method, corrected

**Two attempts died before the current one.**

The first ran a thirteen-section brand survey and went straight to drawing:
twenty-six marks across four rounds, named `lapped-plates`, `modular-grid`,
`stepped-plates`, `rake-is-indent`. All rejected. One of them — `r2-6` — passed
all eleven concept-test questions and was built into a complete identity with
nine documents and a full asset set. **It was still wrong**, because it was a
competent lowercase p that said nothing about pergula.

The diagnosis already existed, about lifeshifter's rodada 5:

> *"Morreu porque um gesto abstrato não tem substantivo. Sem assunto, o olho e o
> modelo encaixam o traço no glifo familiar mais próximo."*

**A survey produces adjectives. A mark needs a noun.** *Trustworthy, precise,
minimalist* describe a mark once it exists; they cannot generate one. lifeshifter's
twenty-two marks were each born from a named idea in its framework — `desvio`,
`teto`, `equalizador`, `alvo` — and its `marks/README.md` says so outright:
*"cada uma nasce de uma parte do framework."*

pergula had no framework document, so there were no nouns to draw from.

**The correction:** write [`concept.md`](concept.md) first — twelve named ideas,
each tied to a line of the source — then the brief, the tokens, the voice, and
only then marks, one per idea. That order is now recorded in
[`README.md`](README.md) and it is the single most important decision in this
folder.

## The mark is *a quebra*

Of twelve marks drawn one-per-idea, the split was clean and instructive:

**The marks about text worked. The marks about objects did not.** `break`,
`reflow`, `quote` and `edge` all read as something about pergula. `boundary`
became an acorn, `session` a luggage tag, `nickname` a bottle, `tail` a comet,
`live` a candle, `permanence` an eye and then a stone in a stream.

That is rodada 6's failure repeating — *"um objeto reconhecível vira ilustração
de banco de imagem, não marca"* — and it happened here **without a raster model**,
which locates the cause more precisely than lifeshifter could:

> **The trap is not the tool. It is asking for an abstraction.** *The boundary*,
> *what stays*, *the live* cannot be drawn directly, so the designer reaches for
> an object to stand in for them — and the object is what you end up owning.

The nouns that produced good marks were the ones already shaped like the thing
they name. *A quebra* is a break in text; you can draw it. *O limite* is a
conviction; you cannot.

**`break` was chosen by the founder** from those four.

## Three lines, not four

Four lines at 64 units gave 2-pixel bars at favicon size, and the break greyed
out. Three lines at 96 units give **exactly 3 real pixels at 16px**, and that one
pixel is the difference between a fracture you can see and a smudge.

Two lines cannot work: the break itself consumes two rows.

The cost, accepted: three lines say "paragraph" less clearly than four.

## A shear, not a chevron

The original `break` ended line 2 in a V and began line 3 with the matching
point. It read as an **arrow** or a play triangle — the most damaging misreading
available, because an arrow means "next" and says nothing about a break.

Six variants attacked this. The diagonal shear keeps the interlock — the two cut
edges are still complementary halves of one line — and cannot be mistaken for a
pointer.

## q4 over q5, and the cost of that

**`q5-gap` is the better-engineered mark.** It removed the chevron entirely
and expressed the break as pure absence: the line stops square, the tail restarts
at exactly that x one row down, and the eye completes the movement itself. At
16px it renders with **two alpha values, 0 and 255 — zero anti-aliasing, unique
in this project.** No misreading is possible because there is no shape to
misread.

**`q4` was chosen anyway**, on presence. At the size this mark actually lives —
a browser tab, a 20px header slot — three pixels of line weight beat two, and the
shear reads as *torn* where q5 reads as *indented*. q5's cost is that at a glance
it passes for a text-alignment icon.

This is a genuine trade and it was made knowingly. `q5-gap` remains in
[`marks/states/`](marks/states/) if robustness ever matters more than presence.

## The alphabet keeps ambushing this vocabulary

Recorded because it recurred four times and will recur again:

- Round one: twelve marks, **every legible one a capital P**, against a brand
  whose name is always lowercase. Cause: the bowl took 60–70% of the height.
- Round three: an **E**, a **reversed E** and two **A's**. Cause: a vertical post
  with horizontal members attached is the anatomy of the Latin alphabet.
- The `q2` variant found a **Z** hiding in the original quebra's down-left slant
  at large sizes; flipping the slant killed it.
- `noise` in the nouns round read as an abstract glyph rather than as a page.

**Check any new variant against the alphabet before anything else.**

Round three also found the escape: **detach the horizontal members from the
vertical**. One designer hit it explicitly — *"first draft with rail 1 touching
the post rendered as a literal E; detaching every rail killed it"* — and it is
true of code as well as of marks. Indented lines do not touch the margin.

## The 32-unit module

512 ÷ 16 = 32. On a 32-unit module every edge lands on a whole pixel at favicon
size. Six of twelve round-one marks blurred at 16px purely because their
coordinates missed that grid.

This is arithmetic, not taste, and it is enforced by the linters in
[`marks/`](marks/) rather than by eye.

## Colour: confirmed by elimination, not by merit

Full proofs in [`color/`](color/). The finding was not what the inheritance
assumed:

**Contrast does not choose lime.** Seven hues at identical lightness and chroma
measure 9.88 to 13.47 on the canvas, rising monotonically toward cyan. On the
dark ground every ramp step from 300 to 800 clears. `#c0e021` earns nothing on
performance.

**It survives because its neighbours are disqualified.** Rotate warm and you
reach Claude's coral family; rotate cool and you reach the neon-on-black look the
survey vetoed. Lime is the only hue in the sweep that is neither — and it holds
exact parity with Battoni Dev's primary-500.

**`#6d8214` is forced, not chosen.** On white, ramp steps 300 through 700 all
fail the 3:1 threshold for graphics; 700 measures 2.86. It is the lightest step
that both passes and still reads as lime.

**The lime buys brand, not legibility.** Ink measures 15.93 on the canvas and
white 18.70 — both far above any colour tested. That is a legitimate purchase and
it should not be described as anything else.

## The lime goes all the way into the product

`--accent` and `--accent-soft` were changed in `pergula` itself, because the CSS
is the source of truth for colour and a `tokens.md` describing a product that
does not exist is worse than no document.

`--accent-soft` moved from `#3a2a21` to `#2a3210`, chosen by measurement: headings
read 11.45 : 1 on it against the original's 11.67, and it sits 1.39 : 1 off the
canvas against the original's 1.36. Same behaviour, different hue.

**The role colours did not move.** `#d97757` stays, because it means *"Claude
spoke"*. Warm for people and Claude, cool for machine is a semantic system, not a
brand one, and it is written as such in the CSS.

## Dark only

Decided 5 September 2026. There will be no light theme. The interface exists for
reading long sessions at length on a second screen, and the warm near-black
ground is part of that.

This does **not** release the mark from working on white. `#6d8214` is still
required: the favicon sits on light browser chrome, the ICO cannot switch, and
the README renders on GitHub's light mode. **The mark works on white; the product
does not.**

## Space Grotesk, outlined

The house sans, so pergula is visibly part of Battoni Dev at no cost.

The shipped lockup carries **outlines, not text** — a wordmark that depends on an
installed font renders wrong on a stranger's README.

The word is fitted **optically**, not by metric match. There is no shared baseline
to match, because the mark is a paragraph and not a letter. Three sizes were
drawn and compared at 260, 300 and 340; 300 balanced.

## The tile exists only outside the logo

The rounded-square container is banned as part of the mark. An apple-touch or PWA
icon has no choice but to be a square, so the rule is narrow: **the tile is a
delivery format for OS icons, never a component of the logo.**

The tiles also re-centre the ink. The mark sits 32 from the top and 64 from the
bottom of its own box — deliberate, because the fallen tail already carries weight
low and right — and inheriting that offset inside a circle or a square would read
as a mistake.

## The favicon is one file

`#c0e021` is 12.40 : 1 on dark browser chrome and 1.51 : 1 on light — invisible.
Rather than ship two assets and keep them in sync, the SVG carries its own
`prefers-color-scheme` query and switches itself. The ICO fallback, which cannot
carry a query, takes the fixed `#6d8214` that clears 4.3 : 1 on **both** grounds.

Both are inlined into `pergula` as data URIs rather than fetched, because the page
makes no network request of any kind — the same reason the Claude mark in the
interface is drawn in JavaScript.
