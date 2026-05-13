# Registrar Guide

Where to actually buy each TLD, with verified pricing patterns and eligibility caveats.

## TLD pricing reference

Prices are approximate USD-equivalent. Confirm at checkout — promotions and premium-tier flagging can change the number.

| TLD              | Cheapest known retail | Typical retail              | Notes                                                |
| ---------------- | --------------------- | --------------------------- | ---------------------------------------------------- |
| `.ai`            | ~$80/yr (2-yr min)    | $80-100/yr                  | Anguilla. No premium tier on most names.             |
| `.dev`           | $15-20/yr             | $15-20/yr                   | Google, HTTPS-required.                              |
| `.app`           | $15-20/yr             | $15-20/yr                   | Google, HTTPS-required.                              |
| `.io`            | $40-60/yr             | $40-60/yr                   | Premium-tier pricing on short names is common.       |
| `.world`         | $25-30/yr             | $25-30/yr                   | Identity Digital gTLD.                               |
| `.build`         | $30 standard          | $30 / $500-$1500 premium    | CentralNic. Many short names are premium-tier.       |
| `.tools`, `.codes`, `.systems`, `.solutions` | $25-30/yr | $25-30/yr     | Identity Digital family.                             |
| `.md`            | nic.md direct: ~$26/yr (450 lei) | $180-$290/yr at international resellers | Moldova. "Medical doctor" premium at international resellers. |
| `.eu`            | ~$5-15/yr             | $5-15/yr                    | EURid. EU/EEA restriction enforced post-registration.|
| `.cz`            | $10-20/yr             | $10-20/yr                   | Czech Republic. Open registration.                   |
| `.de`            | $5-15/yr              | $5-15/yr                    | Germany. Open registration.                          |
| `.foo`, `.bar`   | $25-50/yr             | $25-50/yr                   | Google-operated.                                     |
| `.ge`            | $40-80/yr             | $40-80/yr                   | Georgia. Open registration via accredited registrars.|
| `.rs`            | $15-30/yr             | $15-30/yr                   | Serbia. Open registration.                           |

## Eligibility-restricted TLDs

Some TLDs require proof of presence even though the name appears available:

| TLD              | Requirement                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------------- |
| `.eu`            | EU/EEA citizen, EU/EEA resident, or EU/EEA-based organization. EURid verifies post-registration. |
| `.au`            | Australian individual, organization, or registered Australian trademark.                     |
| `.py`            | Paraguayan presence in most registrar policies (some intermediaries circumvent).             |
| `.bot`           | Verified operation on an approved bot platform (Amazon Lex, MS Bot Framework, Dialogflow).   |
| `.cu`            | Cuban legal presence.                                                                        |
| `.gov`, `.edu`, `.mil` | Sector-restricted (US government, education, military).                                |

Failure to meet eligibility leads to post-registration suspension, not a refund.

## Major registrar coverage

| Registrar      | Strengths                                                                             | Weaknesses                                              |
| -------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Cloudflare     | Wholesale at-cost pricing, no upsells, free DNS at any tier                            | ~390 TLDs only — no `.md`, `.cz`, `.foo`, many ccTLDs   |
| Porkbun        | Wide TLD coverage, transparent pricing, clean checkout UI                              | Doesn't sell `.md`                                      |
| Namecheap      | Aggressive first-year promos                                                           | Renewal usually 2-3× the first-year price               |
| 101domain      | Widest ccTLD coverage of any retail registrar — sells `.md`, `.au`, restricted ccTLDs  | Steeper prices on common TLDs than Cloudflare/Porkbun   |
| Gandi          | EU-friendly, niche ccTLD support                                                       | Many TLDs gated behind paid "Corporate Services"        |
| IONOS          | Promotional first-year on `.eu` / `.de` family                                          | Renewal pricing climbs sharply                          |
| Dynadot        | Mid-range pricing, decent UX                                                           | Uneven ccTLD coverage                                   |

## Registry-direct paths

Open ccTLD registries often sell at wholesale, saving 50-80% over reseller markup:

| TLD     | Registry          | Direct path                                      |
| ------- | ----------------- | ------------------------------------------------ |
| `.md`   | nic.md            | <https://nic.md> — manual email/phone process    |
| `.cz`   | CZ.NIC            | <https://www.nic.cz> or Subreg.cz                |
| `.eu`   | EURid             | Sells via accredited registrars only             |
| `.de`   | DENIC             | Via German registrars (`united-domains`, INWX)   |

## Buying patterns that save real money

- **Single primary TLD on Cloudflare** when it's supported — at-cost, no surprise renewals.
- **Niche ccTLD direct from the registry** when open registration is allowed (`.md`, `.cz`, `.de`). Saves 50-80% over reseller markup.
- **Promotional first-year, transfer at renewal** — Namecheap and IONOS run sub-$5 promos; transfer to a stable registrar before the price jumps.
- **Inquire with local registrars** for country-specific TLDs (Moldovan / Czech / Polish / Belgian / Dutch). Often half the international price.

## When the registry rules don't apply at your registrar

Cloudflare requires its supported TLD list. Porkbun has its own. "Open registration" at the registry doesn't mean every registrar supports it. Cross-check the TLD against the registrar's catalogue before promising a stakeholder a name will be available.
