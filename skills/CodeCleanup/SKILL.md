---
name: CodeCleanup
description: "Proactive code cleanup — duplication removal, pattern adoption, defensive hardening, readability maximization. USE WHEN cleanup, refactor, code quality, reduce duplication, adopt patterns, readability, make code explicit, clean up code, polish code."
---

# CodeCleanup

Proactive, tactical refactoring of working code. The goal is readability, explicitness, and pattern consistency — not feature changes or bug fixes. Complements DefensiveProgramming (principles) and TestDrivenDevelopment (testing discipline) with a concrete workflow.

## Skill Relationships

| Concern | CodeCleanup | Defer to |
|---------|-------------|----------|
| Input validation patterns | Identifies missing guards | DefensiveProgramming |
| Error boundary design | Identifies swallowed errors | DefensiveProgramming |
| Rust-specific idioms | Identifies non-idiomatic Rust | RustDevelopment |
| Test coverage gaps | Flags gaps, does not write tests | TestDrivenDevelopment |
| Naming improvements | Performs the rename | Standalone |
| Function decomposition | Performs the split | Standalone |
| Duplication removal | Performs the merge | Standalone |
| Readability improvements | Performs the edit | Standalone |

---

## Cleanup Categories

### 1. Naming & Self-Documentation

Names ARE the documentation. If code needs a comment to explain what it does, the name is wrong.

**Patterns to apply:**

- **Name-as-documentation**: Function names should read like a sentence fragment. `most_restrictive()`, `find_vault_from_cwd()`, `merge_with_route_config()` need no explanation. `proc()`, `handle()`, `do_thing()` always need one.

- **Verb-first for actions, noun-first for data**: `classify_file()` (action), `parse_level_header()` (action), `Classification` (data), `ProviderAttempt` (data). Mixed conventions within a module are a cleanup signal.

- **Kill the comment, fix the name**: When you see a function with an explaining comment, delete the comment and rename the function to say what the comment said.

```
# Bad — name needs a comment
def check(r):  # check if response has content
    ...

# Good — name IS the documentation
def validate_response_has_content(response):
    ...
```

### 2. Structural Decomposition

Code should be comprehensible without scrolling.

**Patterns to apply:**

- **Screen-fit functions**: Target functions that fit on one screen (~40-50 lines). forge-tlp's vault module is 28 lines total with 3 functions. When a function exceeds 50 lines, look for extractable helpers.

- **One responsibility per file**: Each file should have a clear, singular purpose. A file that handles config loading AND validation AND initialization should be split. Target: under 150 lines per file, under 100 for focused utilities.

- **Thin binaries, thick libraries**: CLI entry points should be thin wrappers that validate args, call library functions, and format output. forge-tlp's `safe-read.rs` is 44 lines — all logic lives in the `redact` library module. Business logic in a binary is a cleanup signal.

- **Private helpers for loop bodies**: When a loop body exceeds 10 lines, extract it into a named helper. The helper's name documents what each iteration does.

### 3. Duplication Elimination

Duplication is the most common cleanup opportunity. Three forms to watch for:

- **Traversal duplication**: Two functions share the same navigation/scanning logic but differ only in what they collect. Extract the traversal into a shared iterator, callback, or higher-order function. Example: forge-tlp's `redact_tlp_sections` and `extract_tlp_blocks` both walk lines looking for `#tlp/red` boundaries.

- **Interface boilerplate**: Subclasses or implementations repeat identical setup/teardown around their unique logic. Extract the repeated part into a base class method, decorator, or wrapper. Example: every provider in lh-model-router checks `if not response.choices: raise ValueError` — this belongs in the base class.

- **Registration over branching**: When an if/elif chain dispatches to handlers based on a string key, replace it with a dict/map lookup. Adding a new handler should require adding one entry, not modifying control flow. Example: lh-model-router's `PROVIDER_CLASSES` dict eliminates a 7-branch if/elif.

### 4. Explicitness & Readability

Code should reveal its intent without requiring the reader to simulate execution.

**Patterns to apply:**

- **Guard clauses over nested ifs**: Validate preconditions at the top and return early. Every level of nesting adds cognitive load. forge-tlp uses `?` for early returns; Python uses early `raise` or `return`.

```rust
// Bad — nested
if let Some(config) = load_config() {
    if config.is_valid() {
        process(config)
    }
}

// Good — guard clauses
let config = load_config()?;
if !config.is_valid() { return Err(...); }
process(config)
```

- **Section markers for visual structure**: In files with multiple logical sections, use visual markers to make the file scannable. Adopt whatever convention the codebase already uses:

```rust
// ─── Diff output ───
fn emit_diff(...) { ... }
fn print_diff_unified(...) { ... }

// ─── Edit mode ───
fn cmd_edit(...) { ... }
```

- **Explicit precedence**: When merge/override logic exists, make the direction explicit. A boolean flag (`obj_precedence: bool`) is clearer than inferring order from call position.

- **Actionable error messages**: Error messages should tell the user HOW to fix the problem, not just WHAT failed. `"Unknown provider 'X' (available: claude, openai, gemini)"` beats `"Invalid provider"`.

### 5. Defensive Hardening

Identify WHERE defensive improvements are needed during cleanup. Apply the actual patterns from DefensiveProgramming.

**Discovery checklist:**

- **Empty collection indexing**: Code that accesses `response.choices[0]` or `items[0]` without checking for empty. SDKs guarantee lists exist but NOT that they contain elements.

- **Swallowed errors**: `let _ = fs::write(...)` or bare `except: pass`. Errors should be logged, propagated, or explicitly documented as intentional.

- **Non-exhaustive matching**: Wildcard `_` catch-all in security-sensitive match arms. New variants will silently pass through.

- **Fail-open defaults**: Security-sensitive config that defaults to permissive on error. forge-tlp defaults to RED (most restrictive) when `.tlp` is unreadable.

---

## Workflow

### Step 1: Scope

Determine what is being cleaned up:

| Scope | Categories that apply |
|-------|----------------------|
| Single file | 1 (naming), 2 (decomposition), 4 (readability), 5 (defense) |
| Module | All five — add 3 (duplication across files) |
| Cross-cutting | All five — add pattern adoption across modules |

If no scope was specified, ask which file or module to clean up.

### Step 2: Inventory

Read every file in scope. Build a table:

| File | Lines | Functions | Longest fn | Notes |
|------|-------|-----------|------------|-------|

Flag files over 150 lines, functions over 50 lines, and any TODO/FIXME markers.

### Step 3: Categorize

Assign each finding to one of the 5 categories. Present as a grouped numbered list. If a finding spans categories, put it in the most specific one.

### Step 4: Sequence

Order changes to minimize conflicts:

1. **Structural decomposition** first — move code before editing it
2. **Duplication elimination** — consolidate before polishing
3. **Pattern adoption** — conform to conventions
4. **Readability** — rename and restructure for clarity
5. **Defensive hardening** — add guards last (operates on stable code)

### Step 5: Execute

Apply changes one category at a time:
- Show before/after for each change
- Run the test suite after each change
- If tests break, fix before continuing
- Confirm with the user between categories

### Step 6: Verify

After all changes:
- Run the full test suite
- Run the linter (`cargo clippy`, `shellcheck`, `ruff`, etc.)
- Present a summary: changes per category, lines added/removed, functions renamed/extracted/merged

---

## Constraints

- Never change behavior — every change must be provably behavior-preserving
- Never combine cleanup with feature work — cleanup is a separate commit
- Never rename public API symbols without grepping all callers first
- Never remove code you don't understand — flag it, don't delete it
- Don't gold-plate — improve the worst code, not polish the best
- Respect existing conventions — if the codebase uses `// ---`, don't introduce `# ===`
- Batch changes — if more than 10 changes, present in groups of 5 with user confirmation between groups
