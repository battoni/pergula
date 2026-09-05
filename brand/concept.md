# pergula — the ideas

> **Draft for correction.** This is the document pergula did not have, written
> out of the source so there is something to argue with. Everything below is
> either **evidenced** — quoted from the code, with a line reference — or marked
> **inferred**, which means I am guessing and you should strike it.
>
> It exists because a brand needs nouns. Adjectives (*trustworthy, precise,
> minimalist*) describe a mark after it exists; they cannot produce one. Every
> mark in lifeshifter was born from a named idea — `desvio`, `teto`,
> `equalizador`, `alvo`. pergula had no such list, so twenty-six marks were
> drawn from geometry instead of from ideas, and none of them had a subject.

---

## The thesis, in the source's own words

> *"Never yank the page while text is selected — that is the whole point here."*
> — `pergula`, the scroll handler

That is the product in one line, and it is a **refusal**, not a feature. pergula
is defined by what it declines to do to you.

The docstring states the problem it exists for:

> *"The terminal renders Claude's prose hard-wrapped, so selecting it with the
> mouse puts real newlines inside every paragraph. This serves the transcripts as
> a plain web page on 127.0.0.1: text selects the way text is supposed to select."*

## The vocabulary

Twelve nouns. Each one is a thing pergula has an opinion about, and each is a
candidate for a mark.

### 1. The break (*a quebra*)

The newline the terminal puts *inside* a paragraph. It is invisible on screen and
fatal on paste: what looked like prose arrives shattered. **Text that is not
text.** This is the enemy the product was built against.

*Evidenced — the docstring.*

### 2. The reflow (*o refluxo*)

Text that flows again to whatever width it is given. Not a feature so much as the
restoration of a property text was supposed to have all along.

*Evidenced — the docstring.*

### 3. The quote (*a citação*)

Lifting a passage out of a session and putting it into an email, an issue, a
document — intact. Every code block carries a copy button; whole messages carry
`copiar tudo`. The product's output is not a file, it is **a quotation**.

*Evidenced — `copiar`, `copiar tudo`, `copiar id` in the interface.*

### 4. The porch (*a varanda*)

What the name means. Latin for the beam structure that throws a light roof out
from a house: a covered place *outside* the building, from which you look back at
what happened inside. The docstring calls it *"a window onto your sessions"*.

*Evidenced — the name and the docstring.*

### 5. The session (*a sessão*)

The unit. It has a name and a colour that **you** gave it with `/rename` and
`/color`, a project, and a moment. pergula does not invent any of that; it reads
what the CLI already wrote.

*Evidenced — `read_tail`, the colour map, `"Later records win: a session can be
renamed or recoloured many times."`*

### 6. The noise (*o ruído*)

The wrappers the CLI injects into user turns that nobody typed:
`system-reminder`, `local-command-stdout`, command names and arguments,
task notifications. pergula strips all of it. **What remains is only what a person
or Claude actually said.**

*Evidenced — `NOISE_PATTERNS`, `"Wrappers the CLI injects into user turns that are
not something the user typed."`*

### 7. The speaker's edge (*a borda de quem fala*)

One hue per role, and a 3px bar down the side that speaks. The rule is written in
the CSS: *"Um tom por papel: quente para gente e Claude, frio para máquina."*
Warm for people and for Claude, cool for the machine. Claude is on the warm side
of that line, deliberately.

*Evidenced — `pergula:555` and the four `--role-*` tokens.*

### 8. The live (*o vivo*)

Which sessions are open in a terminal *right now*. Read from the CLI's own
per-pid registry, never guessed:

> *"It is the only honest answer to 'which sessions are open in a terminal right
> now' — no process table, no reading another process's environment."*

The word in the interface is `ativas`. Note the standard being applied: not "the
best available guess" but **the only honest answer**.

*Evidenced — `LIVE_PATH` and its comment.*

### 9. Permanence (*a permanência*)

pergula's most characteristic rule, and the closest thing it has to a Desvio:

> *"Whatever you are reading stays on the list regardless, so it never vanishes
> under you mid-sentence."*

A session that ends does not disappear from under your eyes. And a finished
session never steals the view from a live one: *"a finished session should not
steal the view."* **The reader's place is protected against the product's own
tidiness.**

*Evidenced — the `ativas` filter and `pick_session`.*

### 10. The machine boundary (*o limite da máquina*)

`127.0.0.1`. No network, no dependency, no build step, no account. The Claude
mark in the interface is *drawn in JavaScript rather than fetched* specifically
so the page makes no request at all:

> *"Drawn here rather than fetched, so the page stays a single file with no
> network at all."*

The LaunchAgent is pinned to `/usr/bin/python3` rather than whatever pyenv is
shimming, *"the agent has to survive a version switch it knows nothing about."*
This is not minimalism as taste. It is **refusal to depend on anything that can
be taken away.**

*Evidenced — the docstring, `AGENT_PYTHON`, `claudeMark`.*

### 11. The nickname (*o apelido*)

Project names you set yourself, stored in a plain JSON file *next to the
transcripts they rename*, "so they survive reinstalls of this script and are
trivial to inspect or delete by hand." **Nothing pergula stores is hidden from
you, and nothing is hard to delete.**

*Evidenced — `NAMES_PATH` and its comment.*

### 12. The tail (*a cauda*)

A long session sends its last four hundred turns; the rest stays one click away.
*"The tail is what anyone is reading anyway."* pergula assumes you are reading
the recent end of a conversation, and optimises for that rather than for
completeness.

*Evidenced — `DEFAULT_LIMIT` and its comment.*

---

## What the vocabulary adds up to

Three convictions run through all twelve, and none of them is a feature.

**Honesty about sources.** Liveness comes from the registry, not the process
table. Names and colours come from the CLI, not from a settings panel. Where
pergula cannot know something, it says so rather than estimating.

**Refusal to depend.** One file, standard library, no network, an interpreter
chosen for survivability. Everything it stores is a plain file you can read and
delete by hand.

**Protecting the reader's place.** Never yank the page while text is selected.
Never let a session vanish mid-sentence. Never let a finished session steal the
view. The product is repeatedly, specifically careful about **not disturbing
someone who is in the middle of reading.**

## Tone, as the interface actually speaks

Every string, lowercase and terse. In English: `filter project or session` ·
`active` · `all` · `follow the live session` · `commands` · `output` ·
`hide list` · `connecting…` · `waiting…` · `no session open in a terminal` ·
`↓ new messages`. The Portuguese reads the same way.

No capitals, no exclamation, no encouragement, no personality. It states what is
and gets out of the way — which is consistent with a product whose central rule
is not to disturb you.

*The interface ships in English and Portuguese, chosen from the sidebar footer
and defaulting to the browser's language. The vocabulary above was first written
in Portuguese, which is why each idea carries its original name in italics — the
file names and the code use the English.*

---

## What is NOT here, and should be

Questions this draft cannot answer from the code:

- **Why you built it.** The docstring gives the technical reason. It does not say
  what made you finally open an editor.
- **Who else is meant to use it**, if anyone, and whether that changes it.
- **What it refuses to become.** The strongest brands here are defined by
  refusals, and yours are visible in the code — but the *list* of things you have
  already decided pergula will never do exists only in your head.
- **Whether there is more product coming**, and whether the vocabulary above is
  the whole of it or the first chapter.
