# pergula — brand survey

> **This file governs.** Where it disagrees with any other document in `brand/`,
> what is written here wins. The one exception is colour: the theme block in
> `pergula` (the `:root` rule around line 548) is the source of truth for every
> hex value, and `tokens.md` is only a readable summary of it.

**Answered by:** Guilherme Battoni
**Date:** 4 September 2026
**Mode:** `fresh` — prior design work in `logos/` was deliberately set aside and
played no part in any answer below.
**Language:** English.

---

## 1. Essence

**Name.** pergula. Always lowercase — in the `<title>`, in the binary name, in
running prose. Never capitalised, never set in caps.

**Meaning.** Latin for the beam structure that throws a light roof out from a
house: the covered porch. The product is that porch — an airy place outside the
terminal from which you look at what happened inside.

**What it is.** A local, dependency-free web reader for Claude Code transcripts.
One Python file, standard library only, bound to `127.0.0.1`.

**The problem it solves.** The terminal renders Claude's prose hard-wrapped, so
selecting it with a mouse puts real newlines inside every paragraph. What looks
like text is not text.

**The transformation.** Text trapped in the terminal becomes real text: it
selects, it copies, it pastes elsewhere without broken reflow.

**The differentiator.** It costs nothing to trust. One file, standard library,
`127.0.0.1`, no build step, nothing leaves the machine — even the Claude mark in
the interface is drawn in JavaScript rather than fetched.

**What would be lost.** The ability to quote Claude: lifting a passage out of a
session and putting it into an email, an issue or a document intact.

## 2. Central concept

**The idea:** shelter over the conversation — a light structure built outside the
terminal so the transcript can be read, and quoted, in the open.

**The metaphor:** beam and post. One member carrying another, the relationship
left visible.

**Visual raw material:** structure — spans and supports. Load-bearing geometry,
no ornament, only what carries.

**The mechanism worth mining:** the speaker's edge. Each message bubble is square
on the side that speaks and rounded on the other three, with a 3px coloured bar
down that edge — a post carrying a body, already living inside the product.

## 3. Personality

**Trustworthy · precise · minimalist · technological.**

- *It should look like* a well-made shelf bracket: you can see what carries what,
  and nothing is present that isn't carrying something.
- *It should never look like* a developer-tool sticker, an AI product launch, or
  enterprise SaaS.
- *If it were a person:* the engineer who leaves the joint exposed.
- *If it were a place:* a covered walkway at night.
- *If it were an object:* a steel shelf bracket.

**Recorded tension.** "Technological" was chosen over "human", while the
product's own colour system deliberately splits warm for people and Claude, cool
for machine. Resolution: *technological* governs the symbol; the warmth stays in
the interface's role colours.

## 4. Audience

Guilherme, and developers who work the same way: one person, many projects,
several parallel Claude sessions. Technical level maximal — the install path is a
Python script and a LaunchAgent. Age band 25–45.

**What keeps it installed:** legibility over long sessions · organisation, finding
the right session fast · speed, it opens and it is there · aesthetics, it is
pleasant to leave open. All four hold.

**Expectation:** a little tuning — theme, visible projects, text size. **This is
why the mark must be genuinely correct on white, not merely survivable.**

**How it should read at a glance:** as craft. One person made this carefully.

**Recorded resolution.** Craft and minimalism do not conflict here, because the
evidence of a hand is the junction itself, left visible rather than tidied away.

## 5. Positioning

**Technical, finished like something premium.** It sits on the shelf with
developer tools and is visibly better made than what is next to it.

**Judged against:** local-first, privacy-respecting tools — Obsidian, Syncthing,
Tailscale, Little Snitch.

**Distance:** completely different from its category.

**Register:** a paid product that happens to be free. Full finish, no
weekend-project signals.

## 6. Symbol

Fully standalone — a favicon, a browser tab, a dock icon and a README avatar all
show it with no name attached. **Abstract, with a logic explainable in one
sentence.** Construction: a **monogram — a lowercase p built from members**.

Must survive 16px. That is a requirement, not a preference.

**Ruled out forever:** the rounded-square container as part of the logo · glow,
gradient, orb, sparkle · the speech bubble.

**Recorded tension.** A monogram is the most common answer in this category, so
being "a p" cannot be the differentiator. The differentiation falls entirely on
*how* the p is built. The test: it must read as a structure that happens to
resolve into a p — post and plate first, letter second.

## 7. Visual language

- **Density:** three or four members, the stem visibly a separate part from the bowl.
- **Corners:** square, every corner at 90°. No radius anywhere. A bracket has no radius.
- **The joint:** lapped — the beam runs over the post and keeps going.
- **The counter:** a clean rectangle, read as the sheltered space under the beam.

> **Amended in phase 4.** The lapped joint proved invisible in a single flat
> colour: two same-coloured members that overlap merge into one silhouette.
> Marks that signalled the lap by overshoot stopped reading as letters at all.
> **The craft signature is now the step** — a visible square offset in the outer
> silhouette — which survives at 16px where the lap does not. See
> [BRAND-DIRECTION.md](BRAND-DIRECTION.md).

## 8. Typography

**Space Grotesk**, medium to semibold, letter stems matched to the mark's member
weight. It is the Battoni Dev house sans; the files ship with the parent brand.

Lockup **horizontal, symbol left**, name right. **The symbol leads; the wordmark
labels it.**

## 9. Colour

**Brand colour: Battoni Dev lime `#c0e021`** (primary-500), `#6d8214`
(primary-800) on light grounds. One flat fill. No gradients.

`--accent` moves to lime throughout the interface. The role colours stay as they
are, because they encode meaning rather than brand: `#d97757` means "Claude
spoke", not "brand".

**Measured, not estimated:**

| | on `#14120f` | on white |
| --- | --- | --- |
| lime `#c0e021` | 12.40 | 1.51 ✗ |
| `#6d8214` | 4.32 | 4.33 ✓ |
| `#4f6010` | 2.68 | 6.97 |
| old accent `#d98b63` | 6.97 | **2.68 ✗** |

Two consequences. pergula's canvas `#14120f` and Battoni Dev's ink `#141413` are
1.01:1 apart — the same colour in practice, so the grounds already agreed. And
the old terracotta accent already failed on white, so the light theme requested
in section 4 forced a colour change regardless of the parent brand.

**Ruled out:** corporate blue · neon or electric *treatment* · purple and violet ·
Anthropic's `#d97757` as a brand colour.

**Recorded resolution.** "No neon on black" was recorded as a restriction on
**treatment, not hue**: no glow, bloom, or outer shadow. Flat lime on flat
near-black is a brand signal, not a sticker.

## 10. References

| Brand | Adapt | Never copy |
| --- | --- | --- |
| Vercel | The discipline of a single primitive — one form, never a second element | The anonymity; a triangle says nothing about the product |
| Arc | Colour confidence: a saturated hue as the whole identity | The playfulness; pergula has no jokes in it |
| Neon | Proof that lime-on-black reads as serious infrastructure | The glow |
| Supabase | An angular monogram that scales without a second version | The gradient inside the mark |

## 11. Competitors

**The competitor is the terminal itself** — a habit, not a product. Direct rivals
are community scripts with no brand at all, which means a real identity is itself
the differentiation.

**Segment default to escape:** dark grey-blue with one electric accent.

**Banned as clichés:** a terminal window with a title bar · a
monospaced-lowercase-wordmark-only identity · a chat bubble · a prompt glyph
(chevron, caret, underscore).

**Distance:** away, decisively.

## 12. Applications and scale

Favicon and browser tab · the page's own header at ~20px · GitHub README header
and repo avatar · a project site or documentation.

**Scale:** 16px is a hard floor. Recognisable with no wordmark.

**Tile:** permitted for OS-level icons only, never inside the logo.

**Favicon rule:** one SVG carrying its own `prefers-color-scheme` query — full
lime on dark chrome, `#6d8214` on light. Fixed `#6d8214` for the ICO fallback.

## 13. Restrictions

**Never:** rounded-square container in the logo · glow, gradient, orb, sparkle ·
speech bubble · terminal window · prompt glyph · monospace-wordmark-only ·
corporate blue · purple · `#d97757` as a brand colour · outline or stroke-only
construction · vines, foliage, sunbeams, or a pergola in perspective.

**Noted risks, not vetoes:** isometric or 3D · shadow and bevel · texture and
grain · the roof or gable reading · the square-bracket or pilcrow reading · the
parking sign.

**One official knockout:** the mark cut out of a solid lime or ink field.

---

## Synthesis — the contract for the design

> Create a visual identity for **pergula**, a local, dependency-free reader for
> Claude Code transcripts, made for developers who run many parallel sessions
> across many projects, whose central proposition is that **text trapped in the
> terminal becomes real text again — selectable, quotable, and kept.** The brand
> must convey **trustworthiness** and **precision**. The symbol must visually
> represent **shelter over the conversation** through **a lowercase p built as a
> structure: square-cut plates, offset and lapped, one member running over
> another with the overlap left visible, and the counter read as the space they
> shelter** — using a **constructed, orthogonal, zero-radius** visual language,
> **Space Grotesk** typography at medium-to-semibold, and a palette of **a single
> flat Battoni Dev lime, `#c0e021` on near-black and `#6d8214` on light**. The
> identity must work as a **16px favicon, a 20px in-app header mark, a GitHub
> avatar, a README header, and a project site**, and remain recognisable at
> **16px with no wordmark at all**. Avoid **the terminal-window icon**, **glow,
> gradient, and any rounded-square container**, and any aesthetic associated with
> **the developer-tool sticker, the AI product launch, and the garden centre**.

## The concept test — eleven questions

Run against the chosen mark, `r2-6-roof-overhang`.

| # | Question | Verdict |
| --- | --- | --- |
| 1 | Does it make sense without the name? | Yes — a square-cut lowercase p |
| 2 | Recognisable at small size? | Yes — verified in real pixels at 16px; counter survives as a clean 3×4px void |
| 3 | Does it belong to the product? | Yes — the plate projecting past the post that carries it is literally what a pergula is |
| 4 | Different enough from competitors? | Yes — nothing in the category is a square lowercase p with a cantilevered roof, and lime is outside the segment palette |
| 5 | Works in black and white? | Yes — one flat fill |
| 6 | Works on light and dark? | Yes — verified at `#c0e021` and `#6d8214` |
| 7 | Simple enough to reproduce? | Yes — four rectangles on a 32-unit module |
| 8 | Recognisable without detail? | Yes |
| 9 | Does the symbol have an explainable logic? | Yes — *a roof plate projecting past the post that carries it, and the space it shelters* |
| 10 | Still makes sense if the product grows? | Yes |
| 11 | Reads as a product mark, not an illustration? | Yes |

**Eleven passes.** It is the only mark of the eighteen explored to clear all
eleven. The two rounds and the reasons the others failed are recorded in
[marks/README.md](../marks/README.md).
