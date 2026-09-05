# pergula — project context

A local, dependency-free web reader for Claude Code transcripts. One executable
Python file, standard library only, bound to `127.0.0.1`.

## The trap: there are two copies

The login agent runs **`~/.local/bin/pergula`**, not this source. Editing the
source changes nothing you can see until you deploy.

```sh
make status    # says whether the installed copy is current or STALE
make deploy    # tests, lints, copies, restarts the agent, waits for the port
```

Never `cp` by hand — `make deploy` runs the checks first, and the agent needs a
`launchctl kickstart` to pick the new file up.

## Layout

| Path | What it is |
| --- | --- |
| `pergula` | The entire product. Python, HTML, CSS and JS in one file |
| `test_pergula.py` | Standard-library tests. `make test` |
| `brand/` | The identity and the reasoning behind it. Start at `brand/concept.md` |
| `brand/marks/` | Every mark explored across four rounds, with the verdict on each |

## Conventions

These are house rules from `battoni.dev/pendulum`, in
`.claude/rules/celer-03-vue-script.md` and `shared-conventions.md`. They apply to
the Python, the JavaScript and the brand scripts alike.

**No `else`.** Early returns, early assigns, or separate `if`s. In a loop, an
early `continue`. This bans `else` branches and wrap-the-whole-body `if` — it
does **not** ban the ternary operator, which may stay for a short terminal
expression.

**Early returns, not wrappers.** `if (!data) return;` then the body, rather than
wrapping the body in `if (data) { ... }`.

**Two or more operands go into a named const.** `const hasModifier = event.metaKey
|| event.ctrlKey; if (!hasModifier) return;` — never the raw condition inline.

**Blank line between distinct instructions.**

**Hygiene.** No `console.*`, no commented-out code, no TODO without a ticket, no
unused anything.

`test_pergula.py` enforces the first and the hygiene ones mechanically, so they
cannot rot.

## Things that are true and easy to break

**The page makes no network request of any kind.** No fonts, no CDN, no
analytics. The Claude mark is drawn in JavaScript rather than fetched; the
favicon and the app icon are inlined as data URIs and base64. Anything that adds
a request breaks the product's central claim.

**The interface ships in English and Portuguese.** Every string lives in
`STRINGS` near the top of the page script. A key added to one language and not
the other renders as its own name — the tests catch it.

**Colour lives in the CSS.** The `:root` block in `pergula` is the source of
truth; `brand/tokens.md` is a readable summary of it. If they disagree, the CSS
wins and the document is stale.

**The mark appears in three places at once** — the sidebar lockup, the tab
favicon and the header at 20px — plus the served `/icon.png`. All four come from
`brand/pergula-icon.svg`; regenerate with `make brand` rather than editing any of
them by hand.

**Transcripts only ever grow.** `parse_transcript` relies on that to parse
incrementally from a saved byte offset. The offset bookkeeping fails silently, so
change it only with the tests in front of you.

## Working on the brand

`brand/concept.md` is the source of truth for the ideas; `brand/BRAND.md` for the
mark's geometry; `brand/BRAND-DIRECTION.md` for why every decision went the way
it did, including the two attempts that were abandoned.

The short version of that history: a brand survey produces **adjectives**, and a
mark needs a **noun**. Twenty-six marks were drawn from geometry and all were
rejected; the one that survived was born from a named idea.
