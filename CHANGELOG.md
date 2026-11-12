# Changelog

Notable changes to pergula. Newest first.

## Unreleased

### Added

- **A Work tab**, the last in the rail: one card per worktree, grouped by
  repository, with stats on top (worktrees, environments up, live sessions, left
  behind). A card shows the status (`active`, `merged · waiting sweep`, `left
  behind`) and `dirty` chips, the stage, branch, commits ahead and uncommitted
  count, the app and API links with the Vite port, the sessions in it (live or
  how long ago), and, for merged and left-behind work, the reason and
  `make wt-down ID=<id>` with a copy button (a toast when the clipboard is
  blocked, a note when `wt-down` would refuse). A click shows the database,
  path and e2e port. The rail filters by text, `active` | `all` and repository.
  It reads `/api/work` once each time the tab opens, with a waiting state for
  the cold answer, and never polls; no control writes anything. At 860px and
  under the rail sits above the cards and long text wraps. Session groups under
  `.claude/worktrees/` carry a `⎇ <worktree>` badge.

- **`GET /api/work`**, the data behind the coming Work tab: one entry per
  worktree (the main checkout left out) of every repository a session ran in.
  Each carries its branch, commits ahead of `origin/main` and the uncommitted
  count from git; the feature title and stage from `specs/<id>-*/`; the links,
  ports and database from its `.worktree.json`, and whether Valet serves it (the
  `api.<label>` link in `~/.config/valet/Sites`); the sessions whose `cwd` is in
  it, live or not, including one that moved in mid-session; and a status:
  `active`, `merged` (its PR is merged, waiting for the sweep) or `left` (PR
  closed unmerged, or seven days with no commit and no session), with the reason
  and `make wt-down ID=<id>` to copy, offered when any checkout of the
  repository has that target (a branch cut before the tooling, or a main that
  has not merged it yet, still has a sibling it runs from). GitHub is asked through `gh pr list`, kept
  five minutes and simply left out when `gh` fails. Read-only: nothing is fetched
  and nothing is changed.

- **A usage tab**: tokens by project and by day, week, month, year or a range of
  dates, counting each response once — not once per line, and not again in
  the files the CLI copies history into (a continued session, a forked
  subagent), which is how a total comes out doubled. The week follows the quota, Saturday 14:00 by default and
  set in the sidebar. Four numbers (tokens, cache read, cache write and output,
  ≈ api equivalent in dollars from a dated price table), three indicators
  (average context, calls over 200k, session base), a stacked bar chart with
  automatic milestones for a new leading model or Claude Code version, a table
  by project and each project's sessions, which open in the reader. Worktrees
  sum in their repository and subagents in their session. The sums live in
  `~/.claude/pergula-usage.json` and outlive the CLI's thirty-day cleanup.
- **Waiting on a shell**, a fifth light. A turn that ends with a shell it is
  waiting on (a CI watch, a build) turns the row purple instead of green, since
  nothing is yours to do yet; it goes back to working when the shell finishes
  and the agent wakes. Dev servers do not count.
- **A snippet library**, for the prompts you send every day that are not worth a
  skill. A second tab in the sidebar manages them; `cmd+K` opens a palette that
  copies one to the clipboard from anywhere in the app. Every turn of your own
  carries a `keep` button that promotes it into the library.
  They are stored as ordinary Markdown under `~/.claude/pergula-snippets/`, one
  file per snippet and one folder deep for grouping, so they stay `grep`-able,
  editable in any editor and versionable. Typing writes the file after a pause;
  retitling moves it.
- **Five favourites**, in their own block at the top of the session list. One
  click copies; the block is there while you read, so the handful of prompts you
  send constantly never needs the library at all. The list lives in
  `~/.claude/pergula-favourites.json`, follows a retitle and forgets a deletion.
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
- **"nada encontrado" no longer appears in the English interface.** The empty
  filter result was the one string that never made it into `STRINGS`.
