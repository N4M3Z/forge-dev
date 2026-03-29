---
paths:
  - "**/*.rs"
---

When validating that a file path stays within an allowed directory, resolve the path to its absolute canonical form first. Raw paths containing `..` components bypass `starts_with()` checks.

In Rust, use `std::fs::canonicalize()`. If it fails (path doesn't exist yet), create the directory first or return an error. Never fall back to the unresolved path for the security check.
