---
paths:
  - "**/*.rs"
  - "**/Cargo.toml"
---

`Result<T, String>` for error handling — no `anyhow`/`thiserror` in forge crates.

`#[forbid(unsafe_code)]` in all crates. Clippy pedantic with `module_name_repetitions`, `must_use_candidate`, `missing_errors_doc`, `missing_panics_doc` allowed.

`cargo fmt` + `cargo clippy -- -D warnings` before committing.
