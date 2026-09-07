# Tokens

Distilled from the `:root` block in `pergula` (around line 538). **The CSS wins.**
If this file and that block disagree, this file is stale.

## Ground and surface

| Role | Token | Value |
| --- | --- | --- |
| Page ground | `--canvas` | `#14120f` |
| Sidebar | `--rail` | `#191614` |
| Panel | `--panel` | `#1c1917` |
| Secondary surface | `--panel-soft` | `#232020` |
| Code blocks and inputs | `--code` | `#12100e` |
| Every border | `--line` | `#322c28` |
| Delete, armed | `--danger` | `#e06c62` |

Warm near-black throughout, not neutral grey. Battoni Dev's ink `#141413` and
this canvas `#14120f` measure 1.01 : 1 apart — the same colour in practice.

## Text

| Token | Value | On canvas |
| --- | --- | --- |
| `--heading` | `#f2ece4` | 15.4 : 1 |
| `--body` | `#ddd5cb` | 12.2 : 1 |
| `--muted` | `#9b8f84` | 5.7 : 1 |
| `--subtle` | `#6f665e` | 2.9 : 1 — decorative only, never body text |

## Brand — held, not settled

| Token | Value | Note |
| --- | --- | --- |
| `--accent` | `#c0e021` | Battoni Dev lime. 12.40 : 1 on canvas |
| `--accent-soft` | `#2a3210` | Active-row tint; headings measure 11.45 : 1 on it |
| — | `#6d8214` | The light-ground value: 4.33 : 1 on white |

`#c0e021` measures **1.51 : 1 on white** and must never be placed there.

**Confirmed 5 September 2026, by comparison.** Proof sheets in
[`color/`](color/). The finding was not what the inheritance assumed:

- **Contrast does not choose lime.** Seven hues at identical lightness and chroma
  measure 9.88 to 13.47 on the canvas, climbing toward cyan. On dark, every ramp
  step from 300 to 800 clears. `#c0e021` earns nothing on performance.
- **It survives by elimination.** Rotate warm and you reach Claude's coral
  family; rotate cool and you reach the neon-on-black look ruled out in the
  survey. Lime is the only hue in the sweep that is neither, and it holds exact
  parity with Battoni Dev's primary-500.
- **The light value is forced, not chosen.** On white, steps 300 through 700 all
  fail the 3:1 threshold for graphics — 700 measures 2.86. `#6d8214` is the
  lightest step that both passes and still reads as lime.
- **The lime buys brand, not legibility.** Ink `#f2ece4` measures 15.93 on the
  canvas and white measures 18.70, both far above any colour tested. That is a
  legitimate purchase, and it should not be described as anything else.

The value it replaced, `#d98b63`, measured **2.68 : 1 on white** — unusable
wherever the mark meets a light ground, which is the favicon, the ICO and the
README. A change was required regardless of the parent brand.

**There is no light theme and there will not be one** (decided 5 September 2026).
`#6d8214` exists for the mark on light grounds, not for a light interface.

## Roles — one hue per speaker

These encode meaning, not brand, and do not move with the accent. The rule is
written in the CSS: *"Um tom por papel: quente para gente e Claude, frio para
máquina."*

| Token | Value | Means |
| --- | --- | --- |
| `--role-you` | `#6fa8d6` | You spoke |
| `--role-claude` | `#d97757` | Claude spoke |
| `--role-tool` | `#85b06b` | A command ran |
| `--role-out` | `#7d746c` | Output came back |

Bubble tints: `--tint-you` `#171d24` · `--tint-claude` `#1f1a17` · `--tint-tool`
`#171c16` · `--tint-out` `#1a1918`.

`#d97757` is Anthropic's coral and is used **because it means Claude**. It is not
a brand colour for pergula, and it never becomes one.

## Typography

| Use | Stack |
| --- | --- |
| Brand | **Space Grotesk** — the house sans, installed with the parent brand |
| Interface body | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` at 15px/1.65 |
| Code | system monospace |
| Speaker labels | 11px, uppercase, `.09em` tracking, weight 600 |

The brand face and the interface face differ on purpose: the interface uses the
system stack so it costs nothing to load and matches the OS it runs on.

## Radius and relief

| Value | Where |
| --- | --- |
| `4px 14px 14px 4px` | Message bubbles — **square on the speaker's edge**, round on the other three |
| `6–10px` | Buttons, inputs, panels |
| `999px` | The primary button only |
| `50%` | The session swatch |

There is no shadow anywhere, and no gradient. Relief is carried entirely by
`--line` borders and one-step background changes. The asymmetric bubble radius is
the most characteristic shape the product already owns — it is *a borda de quem
fala* made geometry.
