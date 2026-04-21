---
name: ShortConfigKeys
version: 0.1.0
description: "Config keys are short and obvious. USE WHEN designing YAML/TOML config schemas."
targets: claude, gemini, codex, opencode
---

`target` not `targetDirectory`. `maps` not `tool_mappings`. If a key needs a comment to explain it, the key name is wrong.

Absence of a value IS the default. Don't add values like `preserve` that mean "do nothing." Just omit the key.
