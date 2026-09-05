# Voice

pergula's voice is already written — it is in the interface, and it is unusually
consistent. This file records it so that anything new sounds like the thing that
exists.

## The rule

**State what is, then get out of the way.**

The product's central conviction is not disturbing someone who is reading. The
voice obeys the same rule: it never asks for attention it does not need.

## How it actually speaks

The interface ships in **English and Portuguese**, picked in the sidebar footer
and defaulting to the browser's language. Every string, in both:

| English | Português |
| --- | --- |
| `filter project or session` | `filtrar projeto ou sessão` |
| `active` · `all` | `ativas` · `todas` |
| `follow the live session` | `seguir a sessão ativa` |
| `commands` · `output` | `comandos` · `saídas` |
| `copy` · `copy all` · `session id · copy` | `copiar` · `copiar tudo` · `ID da sessão · copiar` |
| `hide list` · `show list` | `ocultar lista` · `mostrar lista` |
| `connecting…` · `waiting…` | `conectando…` · `aguardando…` |
| `no session open in a terminal` | `nenhuma sessão aberta no terminal` |
| `no session in the last 2 hours` | `nenhuma sessão nas últimas 2 horas` |
| `↓ new messages` | `↓ novas mensagens` |

A new string is not done until it exists in both. The keys live in `STRINGS` at
the top of the page script; `paintLang()` repaints everything that carries text.

## What that reveals

**Always lowercase.** Including the product name, in the title tag, in the binary,
everywhere. Never capitalised, never in caps.

**Verbs are bare imperatives.** `copiar`, not "copiar para a área de
transferência". `ocultar lista`, not "clique para ocultar a lista".

**Empty states name the condition, not the remedy.** `no session open in a
terminal` says what is true. It does not say "open a session to get started!" —
the product does not instruct you about your own machine.

**No punctuation beyond the ellipsis.** No exclamation marks anywhere. `conectando…`
and `aguardando…` use the ellipsis to mean *this is in progress and you need do
nothing*.

**No first person, no second person.** The interface never says "you" or "your"
and never says "we". The one apparent exception, `você`, is a **role label** for
who spoke — a fact, not an address.

**No encouragement, no streaks, no celebration.** Nothing congratulates you.

## Registers

**Interface — English and Portuguese, lowercase, terse.** As above. Do not add
sentences to it, and never ship a string in one language only.

**Documentation and brand — English, complete sentences, plain.** These files.
Technical claims carry their evidence: a measured contrast ratio, a quoted line,
a file reference. Assertions without evidence are marked as inferred.

**Code comments — English, and they explain *why*.** The existing ones are the
best writing in the project and set the standard: *"the only honest answer to
which sessions are open in a terminal right now — no process table, no reading
another process's environment."* They give the reason, not the mechanism.

## Never

Exclamation marks · imperative encouragement (*let's*, *get started*, *unlock*) ·
capitalising the product name · describing the product as *powerful*, *seamless*,
*beautiful* or *AI-powered* · onboarding copy · empty states that instruct the
user about their own machine · anything that would make a person look up from
what they were reading.
