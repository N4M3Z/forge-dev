# CodeReview

Reference for what a reviewer (human or subagent) should flag, how severity is classified, and how to structure the response. Use as a self-review checklist before requesting review, and as the brief when dispatching a reviewer subagent.

## Severity

| Level | Meaning | Action |
|-------|---------|--------|
| **Critical** | Bug, security issue, data loss path, broken invariant | Fix before merge |
| **Important** | Missed edge case, unclear correctness, weak test, risky refactor | Fix before moving to the next task |
| **Minor** | Style inconsistency, small readability nit, naming | Note for later; do not block |

Anything below Minor is noise — skip it.

## What to look for

### Correctness
- Does the code do what the PR description or plan says?
- Off-by-one, null/None handling, empty collections, unicode edges
- Error paths: are failures propagated or silently swallowed?
- Concurrency: shared state, race conditions, ordering assumptions
- Resource lifecycle: files closed, connections released, contexts exited

### Security
- Untrusted input flowing into shell, SQL, HTML, filesystem paths
- Credentials, tokens, PII in logs or error messages
- Path traversal (`..`), unchecked redirects, deserialization of untrusted payloads
- Authorization checks on every entry point, not just UI

### Tests
- New code covered by at least one test that would fail without it
- Tests test behavior, not implementation
- Fixtures are inert (no real tokens, names, URLs)
- No test disabled or skipped without a linked issue

### Maintainability
- Names describe intent without requiring a comment
- No premature abstraction — three similar lines is fine, two factored into a helper is not
- No half-finished scaffolding, dead branches, or commented-out code
- Cross-file consistency with existing patterns in the same directory

### Docs / changelog
- Public-facing behavior change documented (README, CHANGELOG)
- Breaking changes called out explicitly
- ADRs updated or added where a non-trivial decision was made

## What NOT to flag

- Personal style preferences that don't conflict with project conventions
- Missing refactors that are beyond the PR's scope
- Future-proofing for hypothetical requirements
- Comments that restate the code (leave them; don't expand to a lecture)

## Response format

When reviewing, structure feedback as:

```
Strengths:
- <one or two specific things that work well>

Issues:
  Critical: <file:line — what's broken, why it matters>
  Important: <file:line — what to improve, specific fix>
  Minor: <file:line — short note>

Assessment: Ready to merge | Ready with fixes | Needs rework
```

Be specific: `src/foo.py:42 — missing None check on config.get('port')` beats "error handling could be better."

## When the reviewer is wrong

Push back with evidence, not opinion:

- Point to the test that proves the code works
- Link the convention (rule, ADR) that justifies the approach
- Show the counter-example in the existing codebase

If the reviewer can't refute the evidence, proceed. Reviewers are advisors, not gatekeepers.
