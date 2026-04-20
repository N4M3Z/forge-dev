---
name: RustDevelopment
version: 0.2.0
description: "Rust development conventions — crate structure, error handling, CLI patterns, config loading, testing, and cross-platform compilation. USE WHEN writing Rust code, creating binaries, designing library APIs, or reviewing Rust implementations."
---

# RustDevelopment

## Crate Structure

```
crate/
├── Cargo.toml
├── rustfmt.toml
├── src/
│   ├── lib.rs           # Library crate root
│   ├── main.rs          # Primary binary (coexists with lib.rs)
│   ├── error.rs         # Error + ErrorKind
│   ├── config.rs        # Config with serde + Default + load()
│   ├── cli/             # CLI subcommand handlers (binary-only)
│   ├── <domain>/        # Domain logic
│   │   ├── mod.rs
│   │   └── tests.rs     # Sibling test file
│   └── bin/             # Additional tool binaries
└── tests/               # Integration tests
```

Library code stays pure — no stdout, no `process::exit`, no env access in core logic. Binaries handle I/O boundaries.

Use `src/main.rs` for the primary binary. Use `src/bin/` only for secondary binaries. The primary binary declares its own modules (`mod cli;` resolves to `src/cli/mod.rs`).

## Error Handling

### Structured Errors

Use a structured error type with kind + source chain:

```rust
pub struct Error {
    kind: ErrorKind,
    source: Option<Box<dyn std::error::Error + Send + Sync>>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorKind {
    Parse,
    Config,
    Transport,
}

impl Error {
    pub fn new(kind: ErrorKind) -> Self {
        Self { kind, source: None }
    }

    pub fn with_source(
        kind: ErrorKind,
        source: impl std::error::Error + Send + Sync + 'static,
    ) -> Self {
        Self { kind, source: Some(Box::new(source)) }
    }

    pub fn kind(&self) -> ErrorKind { self.kind }
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", self.kind)?;
        if let Some(ref src) = self.source {
            write!(f, ": {src}")?;
        }
        Ok(())
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        self.source.as_deref()
    }
}
```

Callers branch on `ErrorKind`, not error text. Source errors are preserved for debugging. Make `ErrorKind` `Copy` for cheap comparison.

For internal retry/recovery logic, separate internal errors from public errors:

```rust
pub enum InternalError {
    Transient(std::io::Error),
    Fatal(Error),
}

impl InternalError {
    pub fn is_retryable(&self) -> bool {
        matches!(self, Self::Transient(_))
    }
}
```

### Binary Code

Binaries return `ExitCode`:

```rust
fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("Error: {e}");
            ExitCode::from(1)
        }
    }
}
```

### Never Panic in Libraries

Replace `.unwrap()` with `.unwrap_or_default()`, `?`, or explicit error handling.

## CLI Patterns

Use clap derive with nested enums for subcommands:

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Install {
        #[command(subcommand)]
        target: InstallTarget,
    },
    Validate {
        root: Option<String>,
    },
}
```

Each subcommand dispatches to a handler module returning `ExitCode`. Business logic stays in the library.

## Context Trait

Bundle configuration as associated types in a context trait. Consumers choose concrete implementations; library code is generic:

```rust
pub trait Context {
    type Transport: Send + Sync;
    type Storage: Store;
    type Key: Eq + Hash + Clone + Send + Sync;
}

pub struct Client<C: Context> {
    transport: C::Transport,
    storage: C::Storage,
}
```

Provide stub implementations for testing:

```rust
pub struct StubContext;
impl Context for StubContext {
    type Transport = StubTransport;
    type Storage = InMemoryStore;
    type Key = String;
}
```

## Middleware via Traits

Compose request handling as trait layers:

```rust
pub trait SendRequest<Req, Res> {
    type Err: std::error::Error + Send;
    fn send(&self, req: Req) -> impl Future<Output = Result<Res, Self::Err>>;
}
```

Each middleware wraps a sender and adds behavior:

```rust
pub struct RetryHandler<S: SendRequest<Req, Res>> {
    inner: S,
    max_retries: usize,
}

impl<S: SendRequest<Req, Res>> SendRequest<Req, Res> for RetryHandler<S> {
    async fn send(&self, req: Req) -> Result<Res, Self::Err> {
        // retry logic wrapping self.inner.send(req)
    }
}
```

Layers compose at compile time: `App → Headers → Retry → Timeout → Transport`.

## Type-State Builder

Use type-state generics so the compiler prevents calling `.build()` before required configuration:

```rust
pub struct Builder<Transport = (), Storage = ()> {
    transport: Transport,
    storage: Storage,
    timeout: Duration,
}

impl<S> Builder<(), S> {
    pub fn with_transport(self, t: Http) -> Builder<Http, S> {
        Builder { transport: t, storage: self.storage, timeout: self.timeout }
    }
}

impl<T> Builder<T, ()> {
    pub fn with_storage(self, s: FileStore) -> Builder<T, FileStore> {
        Builder { transport: self.transport, storage: s, timeout: self.timeout }
    }
}

impl Builder<Http, FileStore> {
    pub fn build(self) -> Client { /* only callable when both are set */ }
}
```

No runtime validation, no `Option<T>` fields. Each builder method consumes `self` and returns a new type.

## Sealed Traits

Control who can implement extension-point traits:

```rust
mod internal {
    pub trait Sealed {}
}

pub trait ProvideInfo: internal::Sealed {
    fn fingerprint(&self) -> String;
}

// Only types in this crate can implement Sealed, so only they can implement ProvideInfo.
// For testing, gate an unsealed blanket impl:
#[cfg(feature = "testing")]
impl<T> internal::Sealed for T {}
```

## Config Pattern

Configuration cascade: `config.yaml` (gitignored) overrides `defaults.yaml` (committed) overrides `Default` impl (compiled).

```rust
#[derive(Debug, Deserialize)]
#[serde(default)]
pub struct Config {
    pub database: DatabaseConfig,
    pub server: ServerConfig,
}

impl Config {
    pub fn load(root: &Path) -> Self {
        let path = if root.join("config.yaml").exists() {
            root.join("config.yaml")
        } else {
            root.join("defaults.yaml")
        };

        std::fs::read_to_string(&path)
            .ok()
            .and_then(|c| serde_yaml::from_str(&c).ok())
            .unwrap_or_default()
    }
}
```

## Testing

### Sibling Test Files

```
src/parse/
    mod.rs       # production code
    tests.rs     # #[cfg(test)] mod tests; imported from mod.rs
```

### Rustdoc

Rust has a built-in documentation system — `rustdoc`. Doc comments are markdown. `cargo doc` generates HTML, `cargo test` runs code examples.

Two comment styles:
- `///` on items (functions, structs, enums)
- `//!` at the top of a file (module-level documentation)

Every public function follows this structure:

```rust
/// Split markdown content at `---` frontmatter delimiters.
///
/// Returns `(yaml_text, body)` if frontmatter is found.
/// Returns `None` if the content has no frontmatter.
///
/// # Examples
///
/// ```
/// use commands::parse;
///
/// let content = "---\nname: Test\n---\nBody text";
/// let (yaml, body) = parse::split_frontmatter(content).unwrap();
/// assert!(yaml.contains("name: Test"));
/// ```
///
/// # Errors
///
/// This function does not return errors — it returns `None` instead.
pub fn split_frontmatter(content: &str) -> Option<(&str, &str)>
```

Every module file starts with a `//!` block:

```rust
//! ## Parse
//!
//! Frontmatter extraction from markdown files. Splits content at `---`
//! delimiters and extracts YAML key-value pairs.
```

Standard sections in doc comments:
- Summary line (first line, one sentence)
- Extended description (optional paragraphs)
- `# Examples` — runnable code block (tested by `cargo test --doc`)
- `# Errors` — when the function can fail
- `# Panics` — when the function can panic (should be never per RUST-0001)

### Integration Tests

Use `assert_cmd` for binary-level tests:

```rust
#[test]
fn version_flag() {
    Command::cargo_bin("mytool").unwrap()
        .arg("--version")
        .assert()
        .success();
}
```

### Property-Based Tests

Use `proptest` for functions with large input spaces:

```rust
proptest! {
    #[test]
    fn config_load_never_panics(content in ".*") {
        let _: Config = serde_yaml::from_str(&content).unwrap_or_default();
    }
}
```

## Code Style

### rustfmt.toml

```toml
group_imports = "One"
imports_granularity = "Module"
merge_derives = false
wrap_comments = true
```

### Cargo.toml Lints

```toml
[lints.rust]
unsafe_code = "forbid"

[lints.clippy]
all = { level = "warn", priority = -1 }
pedantic = { level = "warn", priority = -1 }
module_name_repetitions = "allow"
must_use_candidate = "allow"
missing_errors_doc = "allow"
missing_panics_doc = "allow"
```

### `#[must_use]`

Annotate types and functions whose return values should never be silently dropped:

```rust
#[must_use]
pub struct Session { ... }

#[must_use]
pub fn validate(root: &Path) -> Suite { ... }
```

### Feature Flags

Organize hierarchically. Use `dep:` prefix for optional dependencies:

```toml
[features]
default = ["full"]
full = ["cli", "validate"]
cli = ["dep:clap"]
testing = ["dep:tempfile"]
```

### OnceLock for Expensive Init

```rust
fn pattern() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(PATTERN).expect("invalid regex"))
}
```

### General

- `cargo fmt` + `cargo clippy` before every commit
- No `#[allow(unused)]` — remove dead code
- Prefer iterator chains over manual loops
- Use `if let` / `let else` over nested match arms
- Minimize `.clone()` — borrow where possible
- Self-documenting names — comments explain why, not what
- Kebab-case for binary and crate names
- Methods returning `bool` start with `is_` or `has_`
- Full names over abbreviations

## Cross-Platform

- Use `std::path::Path` and `PathBuf` — never string concatenation for paths
- macOS APFS is case-insensitive — never rely on case differences
- `#[cfg(target_os)]` gates for platform-specific APIs


## Additional references

@RustPatterns.md
