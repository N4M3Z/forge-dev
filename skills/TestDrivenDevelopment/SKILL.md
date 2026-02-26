---
name: TestDrivenDevelopment
version: 0.1.0
description: "Test-driven development practices — Red-Green-Refactor cycle, test categories, coverage strategy, property-based testing. USE WHEN writing tests, designing testable APIs, or reviewing test coverage."
---

# TestDrivenDevelopment

Foundational engineering principle for all Forge ecosystem code. Write the test first, then make it pass, then refine.

## The Red-Green-Refactor Cycle

1. **Red** — Write a failing test that describes the desired behavior
2. **Green** — Write the minimum code to make the test pass
3. **Refactor** — Clean up without changing behavior (tests still pass)

This cycle produces code that is testable by design, not testable by accident.

## Test Categories

### Unit Tests

Test individual functions and modules in isolation. These are the backbone:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extract_frontmatter_value_finds_simple_key() {
        let content = "---\ntitle: My Note\nclaude.name: TestAgent\n---\nBody";
        assert_eq!(
            extract_frontmatter_value(content, "claude.name"),
            Some("TestAgent".to_string())
        );
    }

    #[test]
    fn extract_frontmatter_value_handles_quoted_values() {
        let content = "---\ndescription: \"A quoted value\"\n---\n";
        assert_eq!(
            extract_frontmatter_value(content, "description"),
            Some("A quoted value".to_string())
        );
    }

    #[test]
    fn extract_frontmatter_value_returns_none_for_missing() {
        let content = "---\ntitle: Note\n---\n";
        assert_eq!(extract_frontmatter_value(content, "missing"), None);
    }
}
```

**Convention**: Put unit tests in a `tests.rs` file alongside `mod.rs`, referenced by `#[cfg(test)] mod tests;` at the top of the module.

### Integration Tests

Test binary behavior end-to-end. Use `std::process::Command`:

```rust
#[test]
fn safe_read_strips_red_sections() {
    let output = Command::new(env!("CARGO_BIN_EXE_safe-read"))
        .arg("tests/fixtures/mixed-tlp.md")
        .output()
        .expect("failed to run safe-read");

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("## Public Section"));
    assert!(!stdout.contains("#tlp/red"));
    assert!(!stdout.contains("secret content"));
}
```

### Edge Case Tests

Every function should have tests for boundary conditions:

```rust
#[test]
fn handles_empty_input() {
    assert_eq!(extract_frontmatter_value("", "key"), None);
}

#[test]
fn handles_no_frontmatter() {
    assert_eq!(extract_frontmatter_value("Just text", "key"), None);
}

#[test]
fn handles_empty_frontmatter() {
    assert_eq!(extract_frontmatter_value("---\n---\nBody", "key"), None);
}

#[test]
fn handles_frontmatter_without_closing() {
    assert_eq!(extract_frontmatter_value("---\nkey: val\n", "key"), None);
}
```

### Property-Based Tests (when appropriate)

For functions with well-defined invariants, use `proptest` or `quickcheck`:

```rust
#[cfg(test)]
mod proptests {
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn roundtrip_slugify(name in "[A-Z][a-zA-Z]{1,30}") {
            let slug = slugify(&name);
            // slug is always lowercase kebab-case
            assert!(slug.chars().all(|c| c.is_ascii_lowercase() || c == '-'));
            // slug is never empty
            assert!(!slug.is_empty());
        }
    }
}
```

## Test Organization in Forge

### Rust Modules

```
src/
├── frontmatter/
│   ├── mod.rs         # pub fn extract_value(...) + #[cfg(test)] mod tests;
│   └── tests.rs       # all unit tests
├── deploy/
│   ├── mod.rs         # pub fn deploy_agent(...) + #[cfg(test)] mod tests;
│   └── tests.rs       # all unit tests
```

### Shell Test Suites (legacy, being converted)

```
lib/tests/
├── helpers.sh                    # Shared assertions (assert_eq, assert_contains, report)
├── test-module-structure.sh      # Module layout validation
├── test-agent-frontmatter.sh     # Agent file integrity
├── test-defaults-consistency.sh  # Config consistency
├── test-skill-integrity.sh       # Skill file validation
└── test-deploy-parity.sh         # Deploy output matching source
```

Each shell test uses `assert_eq`, `assert_contains`, `assert_file_exists` from helpers and calls `report` to summarize PASS/FAIL.

## Test Fixtures

Use dedicated fixture directories for test data:

```rust
#[test]
fn parses_agent_frontmatter() {
    let content = include_str!("../../tests/fixtures/agent.md");
    let fm = parse_frontmatter(content).expect("valid frontmatter");
    assert_eq!(fm.name, "Developer");
    assert_eq!(fm.model, "sonnet");
}
```

For generated fixtures, create them in test setup:

```rust
fn fixture_agent(name: &str) -> String {
    format!(
        "---\ntitle: {name}\nclaude.name: {name}\nclaude.model: sonnet\n\
         claude.description: \"Test agent\"\nclaude.tools: Read, Grep\n---\n\nBody.\n"
    )
}
```

## Coverage Strategy

| Component | Required Coverage | Method |
|-----------|-------------------|--------|
| Frontmatter parsing | 100% branch | Unit tests with valid/invalid/edge inputs |
| Config loading | All fallback paths | Unit tests with missing/corrupt files |
| Agent deployment | All providers | Integration tests per provider format |
| Skill installation | Happy + error paths | Integration tests |
| TLP redaction | 100% (security-critical) | Unit + property tests |

### What NOT to Test

- External library behavior (serde deserialization, clap parsing)
- Trivial getters/setters with no logic
- Platform-specific code in CI (use `#[cfg]` to skip)

## Test-First Workflow for New Features

1. Write the public API signature with doc comment
2. Write 3-5 tests covering: happy path, error case, edge case
3. Run tests (all fail — Red)
4. Implement the function (tests pass — Green)
5. Refactor for clarity (tests still pass — Refactor)
6. Add any additional edge case tests discovered during implementation

## Running Tests

```bash
# All Rust tests
cargo test --manifest-path Core/Cargo.toml
cargo test --manifest-path Modules/forge-lib/Cargo.toml

# Single test
cargo test --manifest-path <path> -- test_name

# With output
cargo test --manifest-path <path> -- --nocapture

# Shell tests (legacy)
MODULE_ROOT="$(pwd)" bash lib/tests/test-*.sh
```

## Anti-Patterns

| Anti-Pattern | Why | Fix |
|-------------|-----|-----|
| Testing after implementation | Shapes code around existing structure, not behavior | Write test first |
| Testing implementation details | Breaks on refactor | Test public API behavior |
| Large integration tests only | Slow, hard to debug | Unit tests first, integration for wiring |
| Ignoring test failures | Normalizes broken code | Fix immediately or mark `#[ignore]` with reason |
| Copy-paste test cases | Maintenance burden | Use parameterized tests or fixtures |
| Mocking everything | Tests pass but nothing works | Mock at boundaries only |
