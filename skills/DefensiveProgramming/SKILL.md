---
name: DefensiveProgramming
description: "Defensive programming principles for robust systems — input validation, error boundaries, fail-safe defaults, invariant checking. USE WHEN writing production code, designing APIs, handling external input, or reviewing error handling."
---

# Defensive Programming

Foundational engineering principle for all Forge ecosystem code. Every boundary is a potential failure point. Defend it.

## Core Principles

### 1. Validate at Boundaries, Trust Internally

External input (user files, CLI args, env vars, stdin JSON, network responses) is untrusted. Validate it once at the boundary, then pass validated types through internal code:

```rust
// Boundary — validate and convert
let agent_name = validate_agent_name(&raw_input)?;  // returns AgentName (newtype)

// Internal — trust the type
fn deploy_agent(name: &AgentName, dst: &Path) -> Result<()> {
    // name is guaranteed valid — no re-checking needed
}
```

Internal function-to-function calls within the same module can trust their inputs. Don't add redundant validation in every function.

### 2. Fail-Safe Defaults

When configuration is missing or invalid, fall back to safe defaults. Never crash on missing optional config:

```rust
impl Default for Config {
    fn default() -> Self {
        Self {
            max_items: 5,           // conservative default
            strip_red: true,        // security-safe default
            timeout_secs: 30,       // reasonable default
        }
    }
}

// Loading: invalid config → default, not crash
let config: Config = serde_yaml::from_str(&content).unwrap_or_default();
```

**Critical distinction**: Security-sensitive defaults must fail closed. Access control defaults to deny. Everything else fails open.

### 3. Exhaustive Match Arms

Handle every variant. Use `_` as a catch-all only when you've explicitly considered what falls through:

```rust
match exit_code {
    0 => Action::Allow,
    2 => Action::Block,
    _ => Action::Allow,  // fail-open for non-security hooks
}

match tlp_level {
    TlpLevel::Red => Action::Block,
    TlpLevel::Amber => Action::SafeRead,
    TlpLevel::Green | TlpLevel::Clear => Action::Allow,
    // No wildcard — compiler catches new variants
}
```

### 4. Graceful Degradation

When a non-critical subsystem fails, continue without it:

```rust
// Ideas section is optional — missing dir is fine
let ideas_dir = resolve_user(config, cwd, &config.memory.ideas);
if !ideas_dir.is_dir() {
    return None;  // skip section, don't crash
}
```

### 5. Assertive Programming (Debug Assertions)

Use `debug_assert!` for invariants that should never be violated in correct code:

```rust
debug_assert!(!agents.is_empty(), "roster selection produced empty agent list");
debug_assert!(config.max_items > 0, "max_items must be positive");
```

These catch bugs during development but compile away in release builds.

## Error Boundary Patterns

### The Sandwich Pattern

Unsafe (I/O) → Safe (pure logic) → Unsafe (I/O):

```rust
fn main() -> ExitCode {
    // UNSAFE: Read input
    let raw = fs::read_to_string(&path).unwrap_or_default();

    // SAFE: Pure transformation (no I/O, no panics)
    let result = transform(&raw);

    // UNSAFE: Write output
    print!("{result}");
    ExitCode::SUCCESS
}
```

Library code lives in the safe middle. Binaries handle the unsafe edges.

### Error Propagation Strategy

| Context | Strategy |
|---------|----------|
| Library function | Return `Result<T, E>` with descriptive error |
| Binary entry point | Convert to exit code + stderr message |
| Hook handler | Log error, return appropriate exit code |
| Optional feature | `Option<T>` — None means "skip gracefully" |
| Configuration | `unwrap_or_default()` — missing config is normal |

### Never Swallow Errors Silently

```rust
// Bad — error disappears
let _ = fs::write(&path, content);

// Good — log if important, ignore if truly optional
if let Err(e) = fs::write(&path, content) {
    eprintln!("warning: failed to write {}: {e}", path.display());
}
```

## Input Validation Patterns

### Newtype Wrappers for Validated Data

```rust
pub struct AgentName(String);

impl AgentName {
    pub fn new(raw: &str) -> Result<Self, ValidationError> {
        if raw.is_empty() {
            return Err(ValidationError::Empty("agent name"));
        }
        if !raw.chars().all(|c| c.is_alphanumeric()) {
            return Err(ValidationError::InvalidChars("agent name", raw.to_string()));
        }
        Ok(Self(raw.to_string()))
    }

    pub fn as_str(&self) -> &str { &self.0 }
}
```

### Path Traversal Prevention

```rust
fn safe_resolve(base: &Path, relative: &str) -> Option<PathBuf> {
    let resolved = base.join(relative).canonicalize().ok()?;
    if resolved.starts_with(base) {
        Some(resolved)
    } else {
        None  // path escapes base directory
    }
}
```

## Defensive Patterns for Shell Scripts

Forge ecosystem also includes bash scripts. Apply equivalent principles:

```bash
set -euo pipefail              # Fail on error, undefined vars, pipe failures

# Validate inputs
[ -z "${MODULE_ROOT:-}" ] && { echo "MODULE_ROOT not set" >&2; exit 1; }
[ -d "$MODULE_ROOT" ] || { echo "MODULE_ROOT not a directory: $MODULE_ROOT" >&2; exit 1; }

# Use defaults for optional values
MAX_ITEMS="${MAX_ITEMS:-5}"

# Quote everything
deploy_agent "$agent_file" "$dst_dir"
```

## Anti-Patterns

| Anti-Pattern | Why It's Dangerous | Fix |
|-------------|-------------------|-----|
| `.unwrap()` in library code | Panic on unexpected input | Use `?` or `unwrap_or_default()` |
| Ignoring `Result` with `let _` | Silent data loss | Log or propagate |
| String paths instead of `PathBuf` | No OS abstraction, injection risk | Use `Path`/`PathBuf` |
| Trusting file content shape | Malformed files crash the system | Parse with error handling |
| Hard-coded paths | Breaks cross-platform | Use config or env resolution |
| Catch-all `_` in security match | New variant silently passes | Enumerate all variants |
