# pergula — the decisions, and why

Every closed decision with the reason attached. Written so that a year from now
the reasoning is recoverable and a change can be argued with rather than guessed
at.

## The name carries the symbol

*pergula* is Latin for the beam structure that throws a light roof out from a
house. That reading was chosen over three others — the trellis that filters
light, the shopfront that opens to the street, and "it's just a good word". It
won because it gives the symbol something load-bearing to be, and because the
product's own docstring already calls itself a window onto your sessions.

**Consequence:** beam, post and shade are legitimate raw material. Foliage and
perspective are not — the name pulls every designer toward a garden centre, and
that pull is now written down as a ban.

## The symbol is a monogram, against the recommendation

The recommendation was a beam-and-post construction with no letter. A monogram
was chosen instead.

**The cost, accepted knowingly:** monograms are the most common answer in this
category, so being "a p" cannot itself be the differentiator. All of that work
moves to *how* the p is built, and the test became: it must read as a structure
that happens to resolve into a p, never as a letter with structural decoration.

## The craft signature is the step, not the lap

This is the one decision the design work overturned rather than confirmed.

The survey chose a **lapped joint** — the beam running over the post, the overlap
left visible — as the evidence of a hand. It also chose **one flat colour**.
Those two cannot both be honoured: two same-coloured members that overlap do not
show a lap, they merge into a single silhouette.

Twelve marks were drawn before this was provable. Every designer reported it
independently — *"reads more as a stem shoulder than an explicit joint"*, *"the
laps are 1px steps, not countable joints"*, *"at 16px it is a hint, not a
statement"*. The marks that tried to signal the lap by overshooting members
stopped reading as letters at all: one became an **F**, one became **ㅠ**.

**The step survives where the lap does not.** A square offset in the outer
silhouette is visible at 16px because it changes the shape, not the shading. And
in the chosen mark it carries more meaning than the lap ever did: the roof plate
projecting two modules past the post that holds it up is not a joinery detail, it
is the pergola.

## The descender equals the bowl

Round one produced twelve marks and every legible one read as an **uppercase P**,
against a brand whose name is always lowercase. The cause was mechanical: the
bowl took 60–70% of the height and the stem below it 20–30%, which the eye reads
as a capital with a long leg.

A typographic lowercase p runs about 2.4 : 1. This mark runs **1 : 1** — bowl 224
units, descender 224 units. It is not a typographic ratio and it is not meant to
be; it is the ratio at which the mark stops lying about its own name.

## The module is 32 units

Six of twelve round-one marks blurred at 16px, purely because their coordinates
did not land on pixel boundaries. The single mark that stayed crisp was built on
a strict module.

512 ÷ 16 = 32. On a 32-unit module every edge lands on a whole pixel at favicon
size, and the mark rasterises with no anti-aliasing at all. This is arithmetic,
not taste, and it is enforced by `marks/r2-lint.py` rather than by eye.

## The colour comes from the parent brand

The obvious answer was the app's own accent, `#d98b63`. It was rejected in favour
of **Battoni Dev lime `#c0e021`**.

Three things made this right rather than merely convenient:

1. **The old accent was already broken.** `#d98b63` measures **2.68 : 1 on
   white**. The moment a light theme entered scope in section 4, it had to change
   regardless of the parent brand.
2. **It escapes the Claude gravity.** The app's accent and Claude's coral
   `#d97757` are the same clay family; anything in that range reads as "a Claude
   thing" at a glance, which contradicts the explicit choice of *craft* over
   *part of the Claude Code family*.
3. **The grounds already agreed.** pergula's canvas `#14120f` and Battoni Dev's
   ink `#141413` are 1.01 : 1 apart — indistinguishable. No compromise was
   needed.

**The recorded contradiction:** "no neon or electric on black" was vetoed, and
then an acid green on near-black was chosen. Resolved by narrowing the veto to
what it actually meant — **treatment, not hue**. No glow, no bloom, no outer
shadow. Flat lime on flat near-black is a brand signal; the same lime with a halo
is a sticker.

## The lime goes all the way into the product

Not just the mark. `--accent` and `--accent-soft` were changed in `pergula`
itself, because the CSS is the source of truth for colour and a `tokens.md`
describing a product that does not exist is worse than no document.

`--accent-soft` moved from `#3a2a21` to `#2a3210`, chosen by measurement rather
than by eye: headings read 11.45 : 1 on it against the original's 11.67, and it
sits 1.39 : 1 off the canvas against the original's 1.36. Same behaviour,
different hue.

**The role colours did not move.** `#d97757` stays, because it means "Claude
spoke". Warm for people and Claude, cool for machine, is a semantic system, not a
brand one.

## Space Grotesk, and the wordmark is outlined

The survey chose a neutral neo-grotesque — Helvetica or Inter. Space Grotesk is a
grotesque but a characterful one, so this is a small deviation, taken because it
is the house typeface and it makes pergula visibly part of the family at no cost.

The shipped lockup carries **outlines, not text**. A wordmark that depends on an
installed font is a wordmark that renders wrong on a stranger's README.

The word is fitted **optically**, not by metric match. Matching x-heights or
total ink both fail here, because the mark's 1 : 1 bowl-to-descender is not a
typographic proportion — either match makes one element tower over the other.

## The tile exists only outside the logo

The rounded-square container is banned as part of the mark. An apple-touch-icon
or a PWA icon has no choice but to be a square, so the rule is narrow and
explicit: **the tile is a delivery format for OS icons, never a component of the
logo.**

## The favicon is one file

`#c0e021` is 12.40 : 1 on dark browser chrome and 1.51 : 1 on light — invisible.
Rather than ship two assets and keep them in sync, the SVG carries its own
`prefers-color-scheme` query and switches itself. The ICO fallback, which cannot
carry a query, takes the fixed `#6d8214` that clears 4.3 : 1 on **both** grounds.
