---
title: Use Namespaces in Shared Storage
description: Namespace keys with an entity-type prefix in flat key-value stores to prevent silent cross-type collisions
type: adr
category: architecture
tags:
    - architecture
    - storage
    - data
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
upstream: [KeyNamespacing.md]
---

# Use Namespaces in Shared Storage

## Context and Problem Statement

When multiple entity types share a flat key-value store (localStorage, a config map, a JSON lookup), identifiers from different types can collide. For example, an inventory system and a pricing system might both use product code `ITEM001` as a key. If both write to the same store, the second silently overwrites the first. This class of bug is hard to catch in testing because it only manifests when the same identifier exists across entity types — which may be rare in test data but common in production.

## Considered Options

- **Separate stores per entity type** — eliminates collisions but complicates cross-type operations like progress counting and bulk export.
- **Namespaced keys in a single store** — prefix each key with the entity type (`inventory:ITEM001`, `pricing:ITEM001`). One store, zero collisions.
- **Composite keys** (entity type + identifier as a tuple) — semantically correct but awkward in JSON where keys must be strings.

## Decision Outcome

Chosen option: **namespace keys with a short prefix per entity type**. A single shared store with prefixed keys keeps all entries in one object for simple iteration, progress counting, and export — while eliminating cross-type collisions. When retrofitting namespacing onto an existing store, migrate legacy un-prefixed keys on load to avoid silently orphaning saved data. Codified as the `KeyNamespacing` rule.

### Consequences

- [+] Cross-type collisions eliminated by construction
- [+] Single-store iteration and export remain straightforward
- [-] Existing stores require a one-time migration of legacy keys on load
