# pergula — design tokens

> **The code is the source of truth.** These values are read from the `:root`
> block in `pergula` (around line 549). If this file and that block ever
> disagree, **the CSS wins** and this file is stale. Re-read it there before
> relying on a number here.

## Ground and surface

| Token | Value | Role |
| --- | --- | --- |
| `--canvas` | `#14120f` | The page ground |
| `--rail` | `#191614` | Sidebar |
| `--panel` | `#1c1917` | Raised surface |
| `--panel-soft` | `#232020` | Secondary surface |
| `--code` | `#12100e` | Code blocks and inputs, below the canvas |
| `--line` | `#322c28` | Every border |

## Text

| Token | Value | On canvas |
| --- | --- | --- |
| `--heading` | `#f2ece4` | 15.4 : 1 |
| `--body` | `#ddd5cb` | 12.2 : 1 |
| `--muted` | `#9b8f84` | 5.7 : 1 |
| `--subtle` | `#6f665e` | 2.9 : 1 — decorative only, never body text |

## Brand

| Token | Value | Note |
| --- | --- | --- |
| `--accent` | `#c0e021` | Battoni Dev lime, primary-500. 12.40 : 1 on canvas |
| `--accent-soft` | `#2a3210` | Active-row tint. Headings measure 11.45 : 1 on it |
| — | `#6d8214` | primary-800. **The light-ground value**, 4.33 : 1 on white |

`#c0e021` measures **1.51 : 1 on white** and must never be placed there. Any
light ground takes `#6d8214`.

## Roles — one hue per speaker

These encode meaning, not brand, and do not move with the accent. Warm for people
and Claude, cool for machine.

| Token | Value | Means |
| --- | --- | --- |
| `--role-you` | `#6fa8d6` | You spoke |
| `--role-claude` | `#d97757` | Claude spoke |
| `--role-tool` | `#85b06b` | A command ran |
| `--role-out` | `#7d746c` | Output came back |

Each has a matching bubble tint: `--tint-you` `#171d24` · `--tint-claude`
`#1f1a17` · `--tint-tool` `#171c16` · `--tint-out` `#1a1918`.

`#d97757` is Anthropic's coral and is used here **because it means Claude**. It
is explicitly not a brand colour for pergula.

## Typography

| Use | Stack |
| --- | --- |
| Brand and wordmark | **Space Grotesk**, medium to semibold |
| Interface body | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` at 15px/1.65 |
| Code | system monospace |
| Speaker labels | 11px, uppercase, `.09em` tracking, weight 600 |

The brand typeface and the interface typeface are deliberately different: the
interface uses the system stack so it costs nothing to load and matches the OS.

## Radius

| Value | Where |
| --- | --- |
| `0` | **The mark.** Every corner at 90°, always |
| `4px 14px 14px 4px` | Message bubbles — square on the speaker's edge |
| `6–10px` | Buttons, inputs, panels |
| `999px` | The primary button only |

The mark's zero radius is not an oversight: a bracket has no radius, and a small
radius disappears entirely at 16px, so it would be paid for and not received.

## The one shape rule

Every member of the mark is 64 units on a 512 canvas — **2 modules of 32**. At
16px that is exactly 2 real pixels. Nothing in the mark may be drawn off the
32-unit module.
