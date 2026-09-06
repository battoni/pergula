<img src="brand/assets/readme-header.png" alt="pergula" width="512">

A local, dependency-free web reader for Claude Code transcripts.

## The problem

The terminal renders Claude's prose hard-wrapped. Select it with the mouse and
you get real newlines inside every paragraph — so what looked like prose arrives
in your email or your issue tracker shattered.

It looks like text. It is not text.

pergula serves the same transcripts as a plain web page on `127.0.0.1`, where
text selects the way text is supposed to select and every code block has a copy
button.

![Reading a session in pergula](docs/reading.png)

## Install

```sh
curl -fsSLO https://raw.githubusercontent.com/battoni/pergula/main/pergula
chmod +x pergula
./pergula --install
```

`--install` registers a launch agent that runs at login and restarts if it dies.
After that, running `pergula` from any terminal opens the window.

Nothing else is required. One file, the Python standard library, no build step.

## Use

```
pergula              open the window; serve first if nothing is listening
pergula --serve      always serve in the foreground, never just open
pergula --install    run at login as a background agent, restarted if it dies
pergula --uninstall  remove that agent
pergula --status     say whether anything is listening
pergula --port 8080  any of the above, somewhere else
pergula --here       only list sessions from the current directory
```

Default port is `7373`.

## Keyboard

| | |
| --- | --- |
| `cmd/ctrl + B` | hide or show the session list |
| `cmd/ctrl + F` | focus the filter |
| `cmd/ctrl + 1` … `9` | jump to the nth session on the list, in the order shown |
| `esc` in the filter | clear it and let go of it |
| `enter` / `esc` while renaming | keep the project name, or discard it |

Both modifiers are bound on purpose. In an ordinary Chrome tab `cmd+1` belongs to
the tab strip and never reaches the page; only the window pergula opens for
itself is free of that, so `ctrl` is there for everyone else.

Renaming a project starts on a double-click on its name, or on the pencil that
appears when you hover it. Sessions reorder by dragging, and the order is
remembered per project.

Every code block has a copy button, and each message has `copy all`. Both appear
on hover, so they are never in the way of reading.

![The copy button on a code block](docs/copying.png)

## What it shows

A sidebar groups every session by project. Sessions carry the name and the colour
you gave them with `/rename` and `/color`, because the CLI writes both into the
transcript. **active** sessions are the ones with a Claude process open in a
terminal right now — read from the CLI's own per-pid registry in `~/.claude/sessions`, not
guessed from the process table.

Whatever you are reading stays on the list regardless, so it never vanishes under
you mid-sentence. The page never scrolls itself while text is selected.

Project nicknames live in `~/.claude/pergula-names.json`, next to the transcripts
they rename, so they survive reinstalls and are trivial to inspect or delete by
hand.

## The name

*Pergula* is Latin for the light frame of beams that throws a roof out from the
wall of a house — a porch. A covered place **outside** the building, from which
you look back at what happened inside.

That is the product in one word. The work happened in the terminal; this is
where you stand to read it. It is not another room of the house, and it changes
nothing indoors — it only gives you somewhere to sit and look back.

## What it does not do

It never edits, sends, or manages anything. It reads.

Nothing leaves the machine — no account, no sync, no telemetry, no network call
of any kind. Even the Claude mark in the interface is drawn in JavaScript rather
than fetched, so the page makes no request at all.

The `127.0.0.1` binding is deliberate.

## Requirements

macOS, Python 3, and Claude Code writing transcripts to `~/.claude/projects`.

The launch agent runs under `/usr/bin/python3` rather than whatever pyenv happens
to be shimming, so it survives a version switch it knows nothing about. Its log
is at `~/Library/Logs/pergula.log`.

## Licence

MIT — see [`LICENSE`](LICENSE).

The brand is a different matter: the mark and the wordmark identify pergula, and
the licence covers the code, not the identity. Fork the tool freely; give your
fork its own name and its own mark.

## Brand

The mark is a paragraph with a line snapped in two, the tail fallen below — a
picture of the break this exists to fix. [`brand/`](brand/) holds the reasoning,
starting with [`brand/concept.md`](brand/concept.md).
