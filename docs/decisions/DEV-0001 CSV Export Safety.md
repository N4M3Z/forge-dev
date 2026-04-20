---
title: CSV Export Safety
description: Prefix CSV cells starting with formula characters with a tab to prevent spreadsheet formula injection
type: adr
category: security
tags:
    - security
    - csv
    - export
status: accepted
created: 2026-03-04
updated: 2026-03-04
author: "@N4M3Z"
project: forge-dev
related: []
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: []
informed: []
upstream: [CsvExportSafety.md]
---

# CSV Export Safety

## Context and Problem Statement

Any tool exporting CSV for non-technical users faces formula injection risk. If a cell value starts with `=`, `+`, `-`, `@`, or `|`, Excel and LibreOffice interpret it as a formula. Real-world examples: a discount field containing `-20%`, a user comment starting with `+1 doporučuji`, or a chemical product named `@home cleaner`. These are realistic values in inventory, CRM, and POS data that would trigger formula evaluation when the CSV is opened in a spreadsheet.

## Considered Options

- **Strip dangerous characters** — loses data fidelity, alters the original values.
- **Prefix with tab character** — preserves the original value visually while preventing formula evaluation. Tab is invisible in most spreadsheet contexts.
- **Prefix with single quote** — Excel's own escape convention, but the quote is visible in the cell.

## Decision Outcome

Chosen option: **prefix cells starting with `=`, `+`, `-`, `@`, or `|` with a tab character (`\t`)**. Applied at the CSV serialization layer so all exports inherit the protection automatically. Codified as the `CsvExportSafety` rule.

### Consequences

- [+] Formula injection blocked for all exports without data loss
- [+] Tab prefix is invisible in most spreadsheet contexts, preserving user experience
- [-] Tools that parse CSV programmatically must trim leading tabs before using values
