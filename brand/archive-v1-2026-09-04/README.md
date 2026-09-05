> **Abandoned.** This was a complete v1 identity — a square-cut lowercase p —
> built out and then rejected: technically correct, and it said nothing about
> pergula. Only the reasoning is kept; the mark and its assets are gone. The
> shipped identity is one directory up, and
> [`../BRAND-DIRECTION.md`](../BRAND-DIRECTION.md) explains why this one died.

# pergula — brand

The identity, and the reasoning behind it. Nine documents, in reading order.

| File | What it answers |
| --- | --- |
| [BRIEF.md](BRIEF.md) | What the product is, and what it is not |
| [tokens.md](tokens.md) | Palette, typography and radius, read off the real theme |
| [SURVEY.md](SURVEY.md) | **The source of truth.** Thirteen sections answered, the synthesis, the concept test |
| [BRAND.md](BRAND.md) | Specification v1: geometry, measured colour, scale, lockup, limits |
| [BRAND-BRIEF.md](BRAND-BRIEF.md) | Closed brief — self-contained, for briefing a designer |
| [BRAND-DIRECTION.md](BRAND-DIRECTION.md) | Every closed decision and why |
| [image-prompt.md](image-prompt.md) | Prompt, variations, and the selection protocol |
| [marks/README.md](../marks/README.md) | The eighteen marks explored, and which survives 16px |

## Two rules about these files

**[SURVEY.md](SURVEY.md) governs.** Where it disagrees with any other document
here, what is written in the survey wins. It carries the date and the name of
whoever answered it.

**The code is the source of truth for colour.** The `:root` block in `pergula`
(around line 549) holds the real values. [tokens.md](tokens.md) is a readable
summary of that block — if the two ever disagree, **the CSS wins** and the
document is stale.

## The mark

**A roof plate projecting past the post that carries it, and the space it
shelters** — a lowercase p that is really a structure. Four rectangles on a
32-unit module, every corner at 90°, one flat fill.

| File | Use |
| --- | --- |
| `pergula-icon.svg` | The symbol, 512 canvas |
| `pergula-lockup.svg` | Horizontal lockup, wordmark outlined to paths |
| `assets/favicon.svg` | Carries its own `prefers-color-scheme` query |
| `assets/favicon.ico` | 16/32/48, fixed `#6d8214` — legible on both browser chromes |
| `assets/apple-touch-icon.png` | 180 |
| `assets/pwa-192.png`, `assets/pwa-512.png` | Installed-app icons |
| `assets/avatar-512.png` | GitHub |
| `assets/readme-header.png` | 1024 × 512 |
| `assets/pergula-knockout.svg` | The one official reversed form |
| `assets/tile.svg` | Source for the OS tiles — **never a component of the logo** |

Everything in `assets/` is generated from `pergula-icon.svg`. Nothing is drawn by
hand, so the mark cannot drift between surfaces.

## Colour, in one line each

- **`#c0e021`** — Battoni Dev lime. On dark grounds only: 12.40 : 1 on `#14120f`,
  and **1.51 : 1 on white**, where it must never appear.
- **`#6d8214`** — the light-ground value: 4.33 : 1 on white, 4.32 : 1 on dark.
  This is why the ICO, which cannot switch, uses it.
- **`#141413` / `#14120f`** — the ground. Battoni Dev's ink and pergula's canvas
  are 1.01 : 1 apart, which is to say the same colour.
- **`#d97757`** and the other role hues are **not brand colours.** They encode who
  spoke, and they do not move.

## Rebuilding the assets

The application set is generated, not authored. If `pergula-icon.svg` changes,
regenerate rather than editing anything under `assets/`. The mark is four
rectangles; `rsvg-convert` and `magick` do the rest, and
[image-prompt.md](image-prompt.md) records the protocol.

## Checking a new mark

```
python3 marks/r2-lint.py        # module, thickness, colour, banned attributes
python3 marks/contact-sheet.py  # both grounds, in the colour that ships on each
python3 ~/.claude/skills/battoni-new-brand/scripts/size-ladder.py marks
```

The ladder is the one that decides. Half of all marks die at 16px, and a preview
built from `<img width="16">` will not show you which — the browser resamples
smoothly and hides exactly the defect you are looking for.
