# Changelog

Notable changes to pergula. Newest first.

## Unreleased

### Added

- **Language selector.** The interface ships in English and Portuguese, picked in
  the sidebar footer, defaulting to the browser's language.
- **Timestamp on every message**, beside the speaker. Locale-aware, with the date
  shown when the message is not from today and the full stamp on hover.
- **Drag to reorder sessions** within a project. The order persists per project;
  a new session lands at the end. The `cmd+N` shortcuts follow the visible order.
- **Installable as an app.** The server now answers `/manifest.webmanifest` and
  `/icon.png`, so pergula gets its own window and dock icon.
- **The brand.** A complete identity in `brand/` — the mark, the lockup, every
  application asset, and the reasoning across nine documents.
- **Tests.** `test_pergula.py`, standard library only, covering the incremental
  parse, the noise stripping, the state token, the translation table and the
  house conventions.

### Changed

- **Switching sessions is roughly five times faster** — 2236 ms average down to
  403 ms. `onPick` now fetches immediately instead of waiting up to 700 ms for
  the next poll tick.
- **The server no longer re-parses a transcript on every poll.** The response
  token is computed from `stat()`, so an unchanged session answers 204 without
  opening the file: 830 ms down to 5 ms. Parsing is incremental from a saved byte
  offset, and cached for the eight most recent sessions.
- **`--accent` is now Battoni Dev lime** `#c0e021`, confirmed across 33 colour
  proofs rather than inherited. The speaker hues did not move — they encode who
  spoke, not brand.
- The list always opens on **active** sessions.
- Checkboxes are larger and square, in the mark's own language.
- The sidebar carries the lockup; the header mark appears only when the list is
  hidden, so the identity never shows twice.
- The top bar is icons and a tooltip rather than text buttons.
- Code follows the house conventions: no `else`, early returns, named conditions.

### Fixed

- **Renaming a project no longer loses what you typed** when a message arrives.
  The tree refused to redraw during an edit — the guard existed but nothing read
  it. The same guard now covers dragging.
- **A slow response for a session you already left can no longer paint over the
  one you chose.** Each poll carries a run number and stale replies are dropped.
- **A failed clipboard write now says so.** The promise had no `catch`, so a
  refusal looked like nothing happening at all.
