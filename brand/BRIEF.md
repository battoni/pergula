# Brand brief — pergula

Distilled from [`concept.md`](concept.md). Where the two disagree, the concept
document wins.

## The mistake this file exists to prevent

Whoever reads only the code concludes that pergula is a **transcript renderer**,
because rendering is the largest thing in the file — markdown, code fences, copy
buttons, incremental DOM updates. **That is wrong.** Rendering is the cost of
entry, not the product. Every viewer renders.

pergula is a set of **refusals**, and the rendering exists to make them possible.

## What pergula is

A local, dependency-free web reader for Claude Code transcripts. One executable
Python file, standard library only, bound to `127.0.0.1`.

It was built against a specific defect: the terminal hard-wraps Claude's prose,
so selecting it with a mouse puts real newlines inside every paragraph. It looks
like text and it is not text. Paste it anywhere and it arrives shattered.

## The thesis, in the source's own words

> *"Never yank the page while text is selected — that is the whole point here."*

That is the product in one line, and notice that it is stated as a **prohibition**.
pergula is defined by what it declines to do to you.

## The three convictions

Every idea in the vocabulary comes back to one of these. None of them is a
feature.

**Honesty about sources.** Liveness is read from the CLI's own per-pid registry,
never inferred — *"the only honest answer to which sessions are open in a terminal
right now — no process table, no reading another process's environment."* Names
and colours come from what the CLI already wrote, not from a settings panel.
Where pergula cannot know something, it says so instead of estimating.

**Refusal to depend.** One file, standard library, no network, no build step, no
account. The Claude mark in the interface is drawn in JavaScript rather than
fetched, *"so the page stays a single file with no network at all."* The
LaunchAgent is pinned to `/usr/bin/python3` because *"the agent has to survive a
version switch it knows nothing about."* This is not minimalism as taste. It is
refusal to depend on anything that can be taken away.

**Protecting the reader's place.** Never yank the page while text is selected.
Never let a session vanish mid-sentence — *"whatever you are reading stays on the
list regardless."* Never let a finished session steal the view. The product is
repeatedly, specifically careful about not disturbing someone who is in the
middle of reading.

## The vocabulary

Twelve named ideas, defined in [`concept.md`](concept.md):

**the break** the newline inside a paragraph · **the reflow** text that flows
again · **the quote** the passage lifted out intact · **the porch** the covered
place outside · **the session** the named, coloured unit · **the noise** the
injected wrappers, stripped · **the speaker's edge** one hue per role · **the
live** what is open right now · **permanence** what does not vanish under you ·
**the machine boundary** the boundary nothing crosses · **the nickname** the name
you gave, in a file you can delete · **the tail** the recent end, which is what
anyone is reading.

## What pergula is not

**Not a tool.** It never edits, sends, or manages anything. It reads. That
restraint is the product and it is the first thing a competitor would break.

**Not a service.** Nothing leaves the machine. No account, no sync, no telemetry,
no network call of any kind.

**Not an AI product.** It reads Claude's output; it produces none. Borrowing that
visual language would misdescribe it.

**Not a terminal.** Its whole premise is being what you use *instead of* scrolling
back. A mark built from terminal chrome would argue against the product.

**Not for teams.** The `127.0.0.1` binding is a refusal, not an oversight.

**Not light.** Decided 5 September 2026: pergula is dark-only, and there will be
no light theme. The interface is built for reading long sessions on a second
screen at length, and the warm near-black ground is part of that.

This does **not** relax the mark's light-ground requirement. `#6d8214` is still
needed, because the favicon sits on light browser chrome, the ICO cannot switch,
and the README renders on GitHub's light mode. The mark works on white; the
product does not.

## Tone

Every string in the interface is lowercase and terse: `filter project or
session` · `active` · `all` · `follow the live session` · `commands` · `output` ·
`hide list` · `connecting…` · `waiting…` · `no session open in a terminal`.

No capitals, no exclamation, no encouragement, no personality. It states what is
and gets out of the way — consistent with a product whose central rule is not to
disturb you.

The interface ships in **English and Portuguese**, chosen from the sidebar footer
and defaulting to the browser's language. Every string exists in both; see
[`voice.md`](voice.md).

## What already exists

**A parent brand.** Battoni Dev: lime `#c0e021` on ink `#141413`, Space Grotesk
and Sometype Mono, and a custom alphabet built from two offset rounded plates.
The lime is currently in pergula's theme, held pending final confirmation.

**Twenty-six rejected marks**, in [`marks/`](marks/README.md). They failed for one
reason, and it is the same reason lifeshifter's rodada 5 failed: **they had no
subject.** Every one was named after a construction technique — `lapped-plates`,
`modular-grid`, `stepped-plates`, `rake-is-indent` — rather than after an idea.
Without a subject the eye files an abstract shape under the nearest familiar
glyph, which is why round three produced an E, a reversed E and two A's.

This brief exists so that the next marks are born from the twelve nouns above
instead.
