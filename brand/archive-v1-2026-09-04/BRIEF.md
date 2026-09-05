# pergula — what it is, and what it is not

## What it is

A local, dependency-free web reader for Claude Code transcripts. One executable
Python file, 1,721 lines, standard library only, bound to `127.0.0.1`.

It exists because of a specific defect. The terminal renders Claude's prose
hard-wrapped to a fixed column, so selecting it with a mouse puts real newlines
inside every paragraph. Paste that into an email and it arrives shattered. What
looks like text is not text. pergula serves the same transcripts as a plain web
page, where text selects the way text is supposed to select, and every code block
gets a copy button.

Around that it does the obvious adjacent things well. A sidebar groups every
session by project, filterable, with a per-project nickname stored beside the
transcripts it renames. Sessions carry the name and colour set with `/rename` and
`/color`, because the CLI writes both into the transcript. Liveness comes from
the CLI's own per-pid registry in `~/.claude/sessions` — not from the process
table, and not from reading another process's environment. The wrappers the CLI
injects into user turns are stripped, so only the conversation survives. It
installs as a macOS LaunchAgent pinned to `/usr/bin/python3`, deliberately, so a
pyenv switch cannot kill it.

## What it is not

**It is not a tool.** It never edits, sends, manages, or writes anything back
into a session. It reads. That restraint is the product, and it is the first
thing a competitor would break.

**It is not a service.** Nothing leaves the machine. There is no account, no
sync, no telemetry, no network call of any kind — the Claude mark in the
interface is drawn in JavaScript rather than fetched, so the page has no external
dependency at all.

**It is not an AI product.** It reads Claude's output; it does not produce any.
Borrowing the visual language of AI products would misdescribe what it does,
which is why glow, gradient, orb and sparkle are banned outright.

**It is not a terminal.** Its whole premise is being the thing you use *instead
of* scrolling back in the terminal. A mark built from terminal chrome — a window
with a title bar, a prompt glyph, a blinking caret — would argue against the
product.

**It is not for teams.** The `127.0.0.1` binding is a refusal, not an oversight.

## Who it is for

One developer with many projects and several parallel Claude sessions, at maximal
technical comfort — the install path is a Python script and a LaunchAgent, and
the premise assumes a terminal is already open.

## What the brand has to carry

Trustworthy, precise, minimalist, technological — with the finish of a paid
product that happens to be free, and visible evidence that one person made it
carefully. Positioned against local-first tools where "it runs on your machine"
is the point, and deliberately unlike the developer-tool sticker, the AI product
launch, and enterprise SaaS.

The competitor is not another viewer. **It is the habit of scrolling back in the
terminal.**
