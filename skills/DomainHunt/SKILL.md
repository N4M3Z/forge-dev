---
name: DomainHunt
version: 0.1.0
description: "Pick brandable available domains via RDAP, detect broker listings, plan brand families, and choose registrars without overpaying premium tiers. USE WHEN picking a domain, naming a project, checking domain availability, registering a domain, brand research, TLD hack, ccTLD pricing."
---

# DomainHunt

A workflow for picking brandable, available domains without overpaying brokers or premium-tier registries. Wraps the `check-domain` CLI with strategy: candidate generation, RDAP probing, broker detection, brand-family pairing, and registrar selection.

@TldHacks.md
@BrokerDetection.md
@RegistrarGuide.md
@BrandFamilyPairing.md

## Workflow

1. **Frame the brand.** Decide the apex word, the feeling, the audience. A short seed list of 5-10 names is enough — pruning happens at the next step.
2. **Probe with `check-domain`.** Run candidates in parallel against RDAP. Filter on `AVAIL` first, then triage `NO-RDAP` ccTLDs via direct whois.
3. **Detect broker traps.** For interesting `TAKEN` candidates, inspect nameservers. Afternic, Daaz, Dan.com, Sedo, nameshift, and trademarkarea signal active resale (typical ask $500-$50k). See [BrokerDetection.md](BrokerDetection.md).
4. **Look for TLD hacks.** A ccTLD that completes the word (`for.ge` reads as "forge") or a TLD that doubles as a file extension (`.md` for Markdown, `.rs` for Rust) can be the cleverest available solution. See [TldHacks.md](TldHacks.md).
5. **Plan a brand family.** Pick an apex on the strongest TLD and pair companions on thematic or cheap TLDs (`apex.ai` + `apex.dev` + `apex.world`) rather than chasing a single perfect domain. See [BrandFamilyPairing.md](BrandFamilyPairing.md).
6. **Pick registrars.** Verify the registry actually sells each TLD at acceptable prices. Some TLDs (`.md`, `.au`, `.py`) are restricted, gated, or premium-priced even when listed as available. See [RegistrarGuide.md](RegistrarGuide.md).

## The check-domain tool

Location: `bin/check-domain` (bundled with this module) or installed separately from <https://github.com/N4M3Z/check-domain>.

```bash
check-domain example.ai example.dev example.io
check-domain forge.{ai,dev,world,build,tools}
check-domain -q -f candidates.txt
```

The tool queries each TLD's authoritative RDAP endpoint via the IANA bootstrap registry, caches the bootstrap for 24h at `~/.cache/check-domain/`, and runs lookups in parallel.

### Intent-to-flag mapping

| Intent                       | Flag                | Example                                           |
| ---------------------------- | ------------------- | ------------------------------------------------- |
| Check one or several names   | (positional args)   | `check-domain forgeworld.ai forgeworld.dev`       |
| Filter to available only     | `-q` / `--quiet`    | `check-domain -q forge.{ai,dev,build}`            |
| Probe a curated list         | `-f` / `--file`     | `check-domain -f candidates.txt`                  |
| Show usage                   | `-h` / `--help`     | `check-domain --help`                             |

### Output legend

| Status     | Meaning                                                            |
| ---------- | ------------------------------------------------------------------ |
| `AVAIL`    | RDAP returned 404 — not registered                                  |
| `TAKEN`    | RDAP returned 200 — registered (parked or actively used)           |
| `HTTP-XXX` | Registry returned unexpected status (rate limit, throttling)        |
| `NO-RDAP`  | TLD has no public RDAP endpoint — verify manually via whois         |

`NO-RDAP` does not mean available. Common ccTLDs (`.io`, `.sh`, `.so`, `.gg`) lack public RDAP but most popular names on those TLDs are taken — always verify before assuming a `NO-RDAP` is winnable.

## Red Flags

| Thought                                                | Reality                                                                                              |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| "First `AVAIL` hit — done."                            | Premium TLDs (`.build`, `.gold`, `.cars`) often show available but list at $500-$1500. Check checkout. |
| "`NO-RDAP` means I can probably get it."               | Query the ccTLD whois directly. Most desirable names are taken even where RDAP is silent.            |
| "I'll just email the parked owner."                    | Brokered domains have published or quoted asks on the Afternic/Daaz landing page. Read those first.   |
| "Eligibility looks soft — I'll just register."          | `.eu` requires EU/EEA, `.au` requires Australian presence, `.py` is gated. Suspended domains aren't a refund. |
| "One perfect domain solves everything."                | A 3-property brand family on mid-tier TLDs often costs less than one premium domain and reads stronger. |

## Constraints

- Bash, curl, and python3 required for `check-domain` (macOS 12.3+ and most Linux distros ship them).
- RDAP queries are rate-limited per-IP at most registries. For sweeps over 50 domains expect occasional `HTTP-429` and slow the run.
- Brand decisions deserve an ADR — when the result lands on a multi-domain family, capture rationale in the project's `docs/decisions/`.
