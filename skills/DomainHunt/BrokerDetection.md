# Broker Detection

When a domain returns `TAKEN`, the next question is whether it's actively used or parked for sale. The signals below identify the latter.

## Nameserver signatures

The clearest signal is the domain's authoritative nameservers. If they point at a known broker marketplace, the domain is for sale:

| Nameserver pattern                    | Marketplace                              |
| ------------------------------------- | ---------------------------------------- |
| `*.afternic.com`                      | Afternic (GoDaddy's broker arm)          |
| `*.daaz.org`, `daaz.com`              | Daaz                                     |
| `*.dan.com`                           | Dan.com (owned by GoDaddy)               |
| `*.sedo.com`, `*.sedoparking.com`     | Sedo                                     |
| `*.parkingcrew.net`                   | ParkingCrew (often Squadhelp listings)   |
| `nameshift.com`                       | Trademark / brand-protection parking     |
| `trademarkarea.com`                   | Brand-protection parking, often speculation |

Query nameservers with:

```bash
dig @1.1.1.1 +short NS <domain>
```

Or read the `Name Server:` lines in the whois response.

## Registrar signatures

Some registrars are over-represented in speculative holdings:

| Registrar                  | Often signals                              |
| -------------------------- | ------------------------------------------ |
| `Marcaria.com LLC`         | Brand-protection or speculative hold       |
| `Sav.com LLC`              | Discount registrar — frequent flips        |
| `Domains By Proxy LLC`     | Privacy proxy — registrant could be anyone |
| `Network Solutions LLC`    | Legacy holds, low resale interest          |
| `MarkMonitor / CSC`        | Corporate trademark protection — rarely for sale at any reachable price |

## HTTP behavior on the live domain

After identifying broker nameservers, fetch the apex to see the landing:

```bash
curl -sIL --max-time 10 "https://example.ai" | grep -iE "^HTTP|^Location"
```

Common patterns:

| Response                                                | Meaning                                                       |
| ------------------------------------------------------- | ------------------------------------------------------------- |
| `HTTP 405 Method Not Allowed`, no body                  | Parked at broker, no static page                              |
| `HTTP 301/302` to `dan.com/buy-domain/...` or `daaz.com/lander?...` | Explicit marketplace listing                       |
| `HTTP 200` with broker branding                         | Sale page with asking price visible — read before inquiring   |
| `HTTP 200` with substantive content                     | Real site, low resale odds                                    |
| Empty response, connection refused                      | Registered but DNS not configured — could be fresh speculation |

## Typical price ranges by signal class

Asking prices on broker listings vary widely; these are working ranges, not commitments:

| Domain class                                          | Typical Afternic / Daaz ask |
| ----------------------------------------------------- | --------------------------- |
| Common-word `.com` or premium `.ai`                   | $5k - $50k                  |
| Short premium ccTLD (5-letter `.io` or `.md`)          | $1k - $10k                  |
| Recently-registered 4-7 letter speculation             | $500 - $5k                  |
| Domain quietly parked >10 years on private NS          | Variable — open negotiation |

## Acquisition friction signals

Watch for these before committing emotional energy or budget:

- Registrar is a corporate brand-protection service with no public seller — likely held for a corporate trademark, not for resale at any reachable price
- Registration creation date matches the launch of a known speculation pattern (dozens of similar names from the same registrant within a week)
- Nameservers point to a clearly real business — not for sale at any price worth paying
- The domain has a live A record AND a working website — that's a business, not a parked asset

## Inquiry protocol

When a brokered domain is genuinely worth pursuing:

1. Open the apex URL in a browser — many listings show the BIN price or "make offer" floor without authentication.
2. Use the marketplace's inquiry form rather than emailing the registrant directly. Pricing structure and escrow are managed by the marketplace.
3. Start under the visible ask if there is one. Counters of 30-50% of the listed BIN are routine.
4. Budget for transfer fees and escrow (typically $50-200 on top of the price).
