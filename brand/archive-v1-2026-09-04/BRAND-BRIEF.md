# pergula — closed brief

Everything a designer or illustrator needs to work on this identity without
reading the rest of the folder. Self-contained on purpose.

## The product in one paragraph

pergula is a local, dependency-free web reader for Claude Code transcripts. One
Python file, standard library only, bound to `127.0.0.1`. It exists because the
terminal hard-wraps Claude's prose, so copying it out puts real newlines inside
every paragraph — text that is not text. pergula serves the same transcripts as a
web page where text behaves like text. Nothing leaves the machine.

## The brief

> Create a visual identity for **pergula**, a local, dependency-free reader for
> Claude Code transcripts, made for developers who run many parallel sessions
> across many projects, whose central proposition is that **text trapped in the
> terminal becomes real text again — selectable, quotable, and kept.** The brand
> must convey **trustworthiness** and **precision**. The symbol must visually
> represent **shelter over the conversation** through **a lowercase p built as a
> structure**, using a **constructed, orthogonal, zero-radius** visual language,
> **Space Grotesk** typography at medium-to-semibold, and a palette of **a single
> flat lime, `#c0e021` on near-black and `#6d8214` on light**. The identity must
> work as a **16px favicon, a 20px in-app header mark, a GitHub avatar, a README
> header, and a project site**, and remain recognisable at **16px with no
> wordmark at all**.

## Personality

**Trustworthy · precise · minimalist · technological.**

It should look like a well-made shelf bracket — you can see what carries what,
and nothing is present that isn't carrying something. If it were a person: the
engineer who leaves the joint exposed. If it were a place: a covered walkway at
night. If it were an object: a steel shelf bracket.

Positioned as **technical, finished like something premium**, judged against
local-first tools (Obsidian, Syncthing, Tailscale, Little Snitch), reading as a
paid product that happens to be free.

## Non-negotiable constraints

1. **Square corners only.** Every corner at 90°. No radius anywhere in the mark.
2. **One flat fill.** No gradient, no second tone, no stroke, no shadow, no glow.
3. **The 32-unit module.** On a 512 canvas every coordinate is a multiple of 32,
   so at 16px each module is exactly one pixel and the mark rasterises with zero
   anti-aliasing. Members are 64 units — 2 modules.
4. **Lowercase proportion.** The descender must be at least as deep as the bowl.
   This is the single most common failure: at typographic ratios the mark reads
   as a capital P, and the brand name is always lowercase.
5. **A visible step.** The outer silhouette must carry at least one square
   offset, 2 modules deep. This is the craft signature and it replaces a lapped
   joint, which is invisible in a single flat colour.
6. **16px is a hard floor**, and there is only one drawing at every size.

## Banned, without exception

Rounded-square container as part of the logo · glow, gradient, orb, sparkle ·
speech bubble · terminal window with a title bar · chevron, caret, underscore or
any prompt glyph · monospaced-lowercase-wordmark-only identity · corporate blue ·
purple and violet · Anthropic's coral `#d97757` as a brand colour · outline or
stroke-only construction · vines, leaves, sunbeams, or a pergola drawn in
perspective.

## References

**Adapt:** Vercel's discipline of a single primitive · Arc's colour confidence ·
Neon's proof that lime-on-black reads as serious infrastructure · Supabase's
angular monogram scaling without a second version.

**Never copy:** Vercel's anonymity · Arc's playfulness · Neon's glow · Supabase's
in-mark gradient.

## Competitors

The real competitor is **the terminal itself** — a habit, not a product. Direct
rivals are community scripts with no brand at all. The segment default to escape
is dark grey-blue with one electric accent. Move away from it decisively.

## Deliverables

| File | Spec |
| --- | --- |
| Icon | SVG, 512 canvas, `viewBox` only, one flat fill, `<g id="icon">` |
| Lockup | Horizontal, mark left, wordmark outlined to paths |
| Favicon | SVG with its own `prefers-color-scheme` query, plus a fixed-colour ICO |
| OS tiles | 180 / 192 / 512, mark at 62% on `#141413` |
| Knockout | One only — mark cut from a solid lime or ink field |

## How the work will be judged

Rasterised at **96, 32 and 16 real pixels** and magnified with nearest-neighbour.
Not `<img width="16">` — the browser resamples smoothly and hides the defect.
Then against eleven questions, of which the ones that actually kill marks are:
*does it make sense without the name*, *is it recognisable at 16px*, *is it
different enough from the category*, and *does the symbol have a logic you can
state in one sentence*.

Half of all marks die at 16px. Design for that size first.
