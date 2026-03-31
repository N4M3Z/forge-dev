Deserialize YAML, JSON, and TOML into typed structs. Never traverse parsed data with chained `.get()` calls on untyped value objects. Schema mismatches should fail at parse time, not silently return empty defaults.

WRONG — silent failure when schema changes:

```rust
let source = parsed.get("predicate")
    .and_then(|p| p.get("source"))
    .and_then(Value::as_str)
    .unwrap_or("");
```

RIGHT — schema mismatch caught at deserialization:

```rust
let statement: Statement = serde_yaml::from_str(&content)?;
let source = &statement.predicate.source;
```
