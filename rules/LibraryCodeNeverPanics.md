---
paths:
  - "**/*.rs"
---

Library crate code returns `Result` or `Option`. Only binary entry points (`main.rs`, CLI dispatch) may panic on unrecoverable errors. `.expect()` and `.unwrap()` are test-only in library code.

The boundary: if the function is `pub` in a `[lib]` crate, it must not panic. Callers cannot recover from a panic in a dependency.
