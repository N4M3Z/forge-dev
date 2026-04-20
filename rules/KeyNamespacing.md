When multiple entity types share a flat key-value store (localStorage, config map, lookup table), namespace keys by type. Unnamespaced keys collide silently — the last write wins with no error.

```
// Wrong: two entity types share raw identifiers
decisions["ITEM001"] = { action: "merge" };  // storage item
decisions["ITEM001"] = { action: "skip" };   // pricelist item (overwrites)

// Right: prefix by entity type
decisions["storage:ITEM001"] = { action: "merge" };
decisions["pricelist:ITEM001"] = { action: "skip" };
```

If adding namespacing to an existing store, migrate legacy keys on load — otherwise existing data is silently orphaned.
