# Brand Family Pairing

A single domain rarely solves a brand-identity problem. Pairing creates resilience, sub-brand space, and zero-cost expansion through subdomains.

## The apex + companions pattern

Pick one strong apex on a primary TLD, then add sibling TLDs as namespaced product lines:

| Property                       | Role                                              | TLD selected for          |
| ------------------------------ | ------------------------------------------------- | ------------------------- |
| Apex (e.g. `example.ai`)       | Primary marketing site, user-facing identity      | Brand strength + AI signal|
| Companion 1 (e.g. `example.dev`) | Developer docs, CLI / SDK download page          | Dev signal, cheap         |
| Companion 2 (e.g. `example.world`) | Thematic extension, persona sub-brand          | Vibe pairing              |
| Companion 3 (e.g. `example.md`) | Canonical documentation / specification surface   | Markdown signal           |

A coherent 3-property bundle on mid-tier TLDs typically totals under $150/yr — cheaper than one premium single domain and reads as a richer brand.

## Subdomain expansion

Subdomains on an apex you already own cost nothing. After registering `example.ai`, you have:

| Subdomain               | Common purpose                                       |
| ----------------------- | ---------------------------------------------------- |
| `docs.example.ai`       | Documentation                                        |
| `api.example.ai`        | REST surface                                         |
| `ai.example.ai`         | Themed sub-product — fakes the `ai.example` visual   |
| `cli.example.ai`        | Download / installation page                         |
| `blog.example.ai`       | Editorial content                                    |
| `<user>.example.ai`     | Per-user instance (wildcard DNS)                     |

A four-part DNS name reads as a real product surface. Use subdomains liberally before buying another TLD.

## Defensive registration

For a brand you intend to publish under, register the obvious neighbors even when you don't plan to use them:

| Defensive target              | Why                                                                            |
| ----------------------------- | ------------------------------------------------------------------------------ |
| Plural / singular             | `example.ai` plus `examples.ai`                                                |
| Adjacent dev TLDs             | If your apex is `.ai`, also grab `.dev` and `.app`                              |
| Hyphenated variant            | `example-ai.com` for a `.ai` apex                                              |
| Common close-typos            | Rarely worth it unless under active impersonation                              |

Rule of thumb: one apex plus one-to-two defensive registrations is reasonable. Five-plus defensive registrations is bikeshedding unless you're a high-trust brand under active impersonation.

## When to walk away

A brand-family search is failing when:

- Every meaningful TLD is taken, premium-priced, or on a broker
- Adjacent typos are taken by speculators
- The apex name itself triggers a real trademark concern in your sector

Walking away early is cheaper than walking away after registering a partial family. Either rename the brand or scope down to one TLD and lean on subdomains for everything else.

## Trademark posture

Three reasonable defaults when a candidate brand collides with an existing trademark:

| Posture               | When to apply                                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------------------------- |
| Avoid entirely        | Trademark holder is litigious AND your product overlaps their sector                                       |
| Acknowledge and proceed | Trademark holder operates in a fully unrelated sector and the term is sector-specific within that domain |
| Acquire defensively   | The collision is in your sector but the original holder is dormant, willing to sell, or unenforcing        |

The most common mistake is treating trademark risk as binary. A small AI tool sharing a name with a niche miniature line is not the same risk profile as a startup branding itself after a Fortune 500 product. Read the trademark filing — most are sector-scoped — before deciding the name is unusable.
