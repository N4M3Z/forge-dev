---
name: RustDevelopment
version: 0.1.0
description: "Rust development conventions for the Forge ecosystem — crate structure, error handling, CLI patterns, config loading, testing, and cross-platform compilation. USE WHEN writing Rust code, creating binaries, designing library APIs, or reviewing Rust implementations."
---

# RustDevelopment

Forge ecosystem Rust conventions derived from forge-core, forge-tlp, forge-reflect, forge-obsidian, and forge-journals. Follow these patterns for consistency across all modules.

## Crate Structure

Every Rust module follows this layout:

```
module/
├── Cargo.toml           # Package metadata, dependencies, [[bin]] entries
├── rustfmt.toml         # Formatting config (if needed)
├── src/
│   ├── lib.rs           # Library crate root — re-exports public modules
│   ├── config.rs        # Config struct with serde + Default + load()
│   ├── <domain>/        # Domain logic as submodules
│   │   ├── mod.rs       # Module root with #[cfg(test)] mod tests
│   │   └── tests.rs     # Test module (separate file, not inline)
│   └── bin/
│       ├── tool_a.rs    # Binary entry point — thin, delegates to lib
│       └── tool_b.rs    # Each binary is a separate file
└── tests/               # Integration tests (optional)
```

### Binary vs Library Separation

Binaries are thin wrappers. All logic lives in the library crate:

```rust
// src/bin/surface.rs — THIN entry point
use forge_reflect::config::Config;
use forge_reflect::surface;

fn main() -> ExitCode {
    let config = Config::load();
    // delegate to library functions
    if let Some(s) = surface::build_output(&config) {
        print!("{s}");
    }
    ExitCode::SUCCESS
}
```

Library code stays pure — no stdout, no process::exit, no env access in core logic. Binaries handle I/O boundaries.

### Cargo.toml Conventions

```toml
[package]
name = "forge-module"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "tool-name"
path = "src/bin/tool_name.rs"

[dependencies]
serde = { version = "1", features = ["derive"] }
serde_yaml = "0.9"
chrono = { version = "0.4", features = ["serde"] }
regex = "1"
clap = { version = "4", features = ["derive"] }  # only if CLI args needed
```

Use kebab-case for binary names, snake_case for source files.

## Config Pattern

Every module that reads configuration follows this cascade:

```
config.yaml (gitignored override) → defaults.yaml (committed) → Default impl (compiled)
```

```rust
use serde::Deserialize;

#[derive(Debug, Deserialize)]
#[serde(default)]
pub struct Config {
    pub memory: MemoryConfig,
    pub surface: SurfaceConfig,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            memory: MemoryConfig::default(),
            surface: SurfaceConfig::default(),
        }
    }
}

impl Config {
    pub fn load() -> Self {
        let plugin_root = std::env::var("CLAUDE_PLUGIN_ROOT")
            .or_else(|_| std::env::var("FORGE_MODULE_ROOT"))
            .unwrap_or_default();

        // Try config.yaml first, fall back to defaults.yaml
        let config_path = Path::new(&plugin_root).join("config.yaml");
        let defaults_path = Path::new(&plugin_root).join("defaults.yaml");

        let path = if config_path.exists() { &config_path } else { &defaults_path };

        if path.exists() {
            let content = fs::read_to_string(path).unwrap_or_default();
            serde_yaml::from_str(&content).unwrap_or_default()
        } else {
            Self::default()
        }
    }
}
```

### Shared Config (apply_shared)

Modules that consume `defaults.yaml shared:` section wire it through `apply_shared()`:

```rust
pub fn apply_shared(&mut self, shared: &ProjectShared) {
    if self.journal.daily.is_empty() {
        self.journal.daily = shared.journal.daily.clone();
    }
    // ... merge each field, local overrides shared
}
```

## Error Handling

### Library Code

Use `Result<T, E>` with descriptive error types. Prefer `thiserror` for library errors:

```rust
#[derive(Debug, thiserror::Error)]
pub enum ParseError {
    #[error("missing frontmatter delimiter in {path}")]
    MissingDelimiter { path: String },
    #[error("invalid YAML in {path}: {source}")]
    InvalidYaml { path: String, source: serde_yaml::Error },
}
```

### Binary Code

Binaries can use `anyhow` or manual error handling. Most Forge binaries return `ExitCode`:

```rust
fn main() -> ExitCode {
    // ExitCode::SUCCESS for normal operation
    // ExitCode::from(2) for gate/block in hook context
    // ExitCode::FAILURE for fatal errors
}
```

### Never Panic in Libraries

Replace `.unwrap()` with `.unwrap_or_default()`, `?`, or explicit error handling. Panics in library code are bugs.

## CLI Patterns

### Simple Binaries (no clap needed)

Most Forge binaries read stdin (hook JSON) or env vars. No CLI args:

```rust
fn main() -> ExitCode {
    let config = Config::load();
    let input = read_hook_input().unwrap_or_default();
    // ...
}
```

### Complex Binaries (use clap)

When CLI args are needed, use clap derive:

```rust
use clap::Parser;

#[derive(Parser)]
#[command(name = "safe-read")]
struct Cli {
    /// File to read
    file: PathBuf,
    /// Strip TLP-red sections
    #[arg(long, default_value_t = true)]
    strip_red: bool,
}
```

## Lazy Static Patterns

Use `OnceLock` for compiled regex and other expensive initialization:

```rust
use std::sync::OnceLock;

fn secret_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(SECRET_PATTERNS).expect("invalid regex"))
}
```

## YAML Frontmatter Parsing

The canonical pattern for parsing markdown frontmatter in Rust:

```rust
pub fn extract_frontmatter_value(content: &str, key: &str) -> Option<String> {
    let mut in_frontmatter = false;
    for line in content.lines() {
        if line.trim() == "---" {
            if in_frontmatter { return None; } // end of frontmatter
            in_frontmatter = true;
            continue;
        }
        if in_frontmatter {
            if let Some(rest) = line.strip_prefix(&format!("{key}:")) {
                let val = rest.trim().trim_matches('"').trim_matches('\'');
                return Some(val.to_string());
            }
        }
    }
    None
}
```

For full YAML parsing, deserialize with serde_yaml. For simple key extraction (hooks, quick checks), use line-by-line parsing to avoid pulling in the full YAML parser.

### Frontmatter vs Plain YAML

`fm_value` (from `parse` module) expects markdown frontmatter delimiters (`---`). For plain YAML files like `module.yaml` or `defaults.yaml`, use a line-by-line `yaml_value` helper instead — `fm_value` silently returns `None` on non-frontmatter YAML:

```rust
fn yaml_value<'a>(content: &'a str, key: &str) -> Option<&'a str> {
    let prefix = format!("{key}:");
    content.lines()
        .find(|l| l.starts_with(&prefix))
        .and_then(|l| l.get(prefix.len()..))
        .map(|v| v.trim().trim_matches('"').trim_matches('\''))
}
```

For nested YAML or complex structures, use `serde_yaml::from_str::<serde_yaml::Value>()` and navigate with `Value::as_mapping()` / `Mapping::get()`.

## Cross-Platform Considerations

### Path Handling

Always use `std::path::Path` and `PathBuf`. Never construct paths with string concatenation:

```rust
// Good
let config_path = root.join("config.yaml");

// Bad
let config_path = format!("{}/config.yaml", root);
```

### File System

- Use `Path::exists()` not shell `test -f`
- Use `fs::read_dir()` with proper error handling
- macOS APFS is case-insensitive by default — never rely on case differences
- Handle missing directories gracefully (create if needed, skip if optional)

### Build Targets

Forge binaries must compile on:
- macOS (primary development platform)
- Linux (CI/CD, server deployments)
- Windows (future, via cross-compilation)

Avoid platform-specific APIs unless behind `#[cfg(target_os)]` gates.

## Module Integration

### Hook Input

Hook binaries read Claude Code's JSON payload from stdin:

```rust
pub fn read_hook_input() -> Option<HookInput> {
    let stdin = std::io::stdin();
    let input: HookInput = serde_json::from_reader(stdin.lock()).ok()?;
    Some(input)
}
```

### Exit Codes

| Code | Meaning | Used by |
|------|---------|---------|
| 0 | Success / allow | All hooks |
| 1 | Error (non-blocking) | Passive hooks |
| 2 | Block / deny | Gate hooks (PreToolUse, Stop) |

## Validation Pattern (validate-module)

forge-lib provides a `validate` module pattern for convention checking: pure library functions return `Vec<Check>` results, a thin CLI binary handles formatting. The `Suite` struct provides assertion helpers (`assert_eq`, `assert_contains`, `assert_match`, `assert_file_exists`, `assert_not_empty`).

```rust
pub struct Check { pub desc: String, pub passed: bool }
pub struct Suite { pub name: String, pub checks: Vec<Check> }

// Pure validation function — no I/O beyond reading module files
pub fn validate_structure(root: &Path) -> Suite { ... }
```

Consumer modules wire it via Makefile: `$(LIB_DIR)/bin/validate-module $(CURDIR)`.

## Code Style

- `cargo fmt` before every commit
- `cargo clippy` with no warnings
- No `#[allow(unused)]` — remove dead code
- Prefer iterator chains over manual loops
- Use `if let` / `let else` over nested match arms
- Minimize `.clone()` — borrow where possible
- Self-documenting names — comments explain why, not what
