---
title: Forge Ecosystem Domain Identity
description: Choose a brand-family of domains for the forge ecosystem (apex + sub-brands + thematic TLDs) without paying broker premiums or premium-tier traps
type: adr
category: governance
tags:
    - governance
    - branding
    - domains
status: accepted
created: 2026-05-13
updated: 2026-05-13
author: "@N4M3Z"
project: forge-dev
related: []
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: []
informed: []
upstream: [DomainHunt]
---

# Forge Ecosystem Domain Identity

## Context and Problem Statement

The forge ecosystem (CLI binary, library, ~30 published modules, public documentation) needs a coherent web-property identity. The natural apex `forge.ai` is held by a private 2017 GoDaddy registration with no live site — broker-acquirable but not at base price (typical short `.ai` resale ranges $5k-$50k). Every follow-on candidate explored — `forge.dev`, `forge.io`, `forge.app`, every `forgehq.ai` / `forgekit.ai` / `useforge.ai` modifier — is taken. The technically-available `forge.build` is priced as a premium-tier `.build` registration at $1,500.

The ecosystem needs a pronounceable apex, room for product-line sub-brands, a multi-TLD family totalling under $200/yr, and a trademark posture compatible with public publishing.

## Decision Drivers

- Brand alignment with the ecosystem's purpose (module-building, agent forging, skill authoring)
- Available without paying broker premium ($5k-$50k typical for `.ai` shorts)
- Available without premium-tier TLD traps ($500+ for short names on `.build`, `.gold`, `.cars`)
- Coherent multi-property family supporting product-line differentiation
- No live trademark conflicts in the AI-tooling sector
- Affordable annual renewal across the bundle

## Considered Options

- **Acquire `forge.ai` from broker** — pay $5k-$50k+ for the canonical apex
- **Buy `forge.build`** — premium-tier `.build` at $1,500 first-year
- **Single-modifier `.ai`** (`forgehq.ai`, `forgekit.ai`, `useforge.ai`, `agentforge.ai`) — every variant probed, all taken
- **Latin or mythological alternative** — `caminus.dev` (literal Latin "forge"), `mulciber.ai` (Vulcan's epithet); both available
- **Foreign-language smithy/anvil** — `kovarna.ai` (Czech smithy), `bigorna.ai` (Portuguese anvil), `enclume.ai` (French anvil)
- **Compound on `.ai` with a thematic apex word** — `forgeworld.ai`, `modforge.ai`, `handforged.ai`; all available
- **TLD-hack apex** — `for.ge` was cleanest but held by a Georgian non-profit since 2011

## Decision Outcome

Chosen: **a multi-property brand family centered on `forgeworld.ai` as the public apex, with `modforge.*` and `handforged.*` as sub-brand product lines.**

`forgeworld.ai` is the marketing apex. The Forge World name resonates in two directions — as Games Workshop's specialist miniature studio and as the in-universe Adeptus Mechanicus planet class that houses imperial weapons forges. Both senses imply specialist craft and deliberate construction, which matches an AI tooling ecosystem that builds skills, agents, and modules with care.

`modforge.ai` plus `modforge.dev` plus `modforge.world` carries the module-ecosystem sub-brand. "Mod-forge" directly describes what the forge ecosystem produces: composable modules of skills, agents, and rules. The Minecraft "ModForge" modding loader is a collision but in a fully separate audience.

`handforged.ai` is reserved for hand-curated, premium-quality skill and agent libraries. "Hand-forged" reads artisanal and counterpoints `modforge` (which connotes batch production) with quality framing.

Rejected:

- **Broker acquisition of `forge.ai`** — the price-to-value ratio over `forgeworld.ai` does not justify the broker tax
- **`forge.build` at $1,500** — premium-tier trap; the same brand identity assembles coherently on standard-tier TLDs for under $200/yr total
- **Foreign-language alternatives** (caminus, mulciber, kovarna) — strong individually but lose audience clarity in the predominantly English AI-tooling discourse
- **`for.ge` TLD hack** — owned by an active Georgian non-profit (Union Press); low practical acquisition odds

### Trademark posture

"Forge World" is a registered trademark of Games Workshop Group plc, scoped to miniature wargaming and adjacent merchandise. Practical risk is low: Games Workshop has pursued trademark adjacency in its own sector (the [Space Marine](https://en.wikipedia.org/wiki/Space_Marine_trademark_dispute) dispute being the high-water mark) but has not pursued cross-sector uses of "Forge World" as a phrase. AI tooling is fully outside the trademark's covered sector.

Acceptable risk; documented.

### Acquisition plan

| Domain                | Registrar (preferred)          | Approx price/yr  |
| --------------------- | ------------------------------ | ---------------- |
| `forgeworld.ai`       | Cloudflare or Porkbun          | ~$80-100         |
| `modforge.ai`         | Cloudflare or Porkbun          | ~$80-100         |
| `modforge.dev`        | Cloudflare                     | ~$15-20          |
| `modforge.world`      | Porkbun or 101domain           | ~$25-30          |
| `handforged.ai`       | Cloudflare or Porkbun          | ~$80-100         |

Total annual: ~$280-350 across the family.

## Consequences

- [+] Coherent multi-domain brand family totalling under $350/yr — affordable defense and product-line space
- [+] Apex plus sub-brand structure supports product and persona differentiation without paying broker premiums
- [+] No broker tax, no premium-tier trap
- [+] Pronounceable, memorable across the family
- [+] Subdomain expansion on each apex (e.g. `ai.forgeworld.ai`, `docs.modforge.dev`) extends the family at zero additional registration cost
- [-] Mild Games Workshop trademark adjacency on `forgeworld.ai` (low practical risk given sector separation)
- [-] `modforge` collides with the Minecraft modding loader of the same name (different audience, low practical confusion)
- [-] Multi-domain family requires DNS discipline — pick a primary registrar and manage uniformly to avoid renewal drift

Future TLDs in this family inherit the same pattern. Decisions to deviate (broker acquisitions, premium-tier purchases, new sub-brand additions) belong in subsequent ADRs.
