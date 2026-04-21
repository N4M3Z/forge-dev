---
title: GitHub Documentation Files
description: Include GitHub community health files based on repository audience, with a two-file convention for multilingual READMEs
type: adr
category: governance
tags:
    - governance
    - documentation
    - github
status: accepted
created: 2026-03-16
updated: 2026-03-16
author: "@N4M3Z"
project: forge-dev
related: []
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: []
informed: []
upstream: [GitHubDocumentationFiles.md]
---

# GitHub Documentation Files

## Context and Problem Statement

GitHub automatically detects specific filenames and surfaces them in the repository UI — tabs, sidebar links, PR helpers, and issue templates. Not including these files means missing free discoverability that GitHub provides. The question is which files every repo should have and how to handle multilingual content.

## Considered Options

- **Minimum set** — README + LICENSE only. Simple but misses CONTRIBUTING (shown in PR flow) and SECURITY (gets its own tab).
- **Full set** — all community health files. Overhead for small private repos that don't need CODE_OF_CONDUCT or FUNDING.
- **Audience-based** — include files based on the repo's audience (private team vs public contributors). Each file earns its place.

## Decision Outcome

Chosen option: **audience-based**, because private repos don't need FUNDING or CODE_OF_CONDUCT but every repo benefits from README, LICENSE, and CONTRIBUTING.

### Minimum (all repos)

README.md, LICENSE, CONTRIBUTING.md

### Public repos add

CODE_OF_CONDUCT.md, SECURITY.md, SUPPORT.md

### Multilingual READMEs

GitHub does not support native language switching. The community convention is two files with a language switcher link at the top:

```text
README.md      — primary language
README.cs.md   — ISO 639-1 code suffix
```

Each file starts with a flag-based switcher line:

```markdown
🇬🇧 English | [🇨🇿 Česky](README.cs.md)
```

GitHub renders README.md by default. The translated file is a regular file visible in the file list, linked from the primary README.

## Consequences

- Every new repo gets README + LICENSE + CONTRIBUTING at creation
- Public repos get the full set via `.github/` org-level defaults
- Multilingual repos use the two-file pattern with ISO 639-1 suffixes
- CITATION.cff is only for research/academic projects — not required by default
