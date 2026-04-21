---
paths:
  - "**/*.rs"
---

Never silently erase errors from I/O operations. `.unwrap_or_default()` on file reads, network calls, or deserialization hides corruption and data loss. Either propagate the error or log it before falling back.

A corrupt config parsed with `.unwrap_or_default()` becomes an empty config with no warning. The user sees wrong behavior with no indication of why.
