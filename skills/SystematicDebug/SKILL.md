---
name: SystematicDebug
version: 0.1.0
description: "Four-phase debugging methodology — root cause before fixes. USE WHEN encountering any bug, test failure, unexpected behavior, or build failure."
---

# SystematicDebug

Find the root cause before attempting fixes. Random fixes waste time and create new bugs.

## The Four Phases

Complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

Before attempting any fix:

1. **Read error messages carefully** — don't skip past errors. They often contain the exact solution. Read stack traces completely. Note line numbers, file paths, error codes.
2. **Clarify the failure mode when the report comes from the user.** "Doesn't work" is ambiguous — before forming hypotheses, ask one question naming the candidate layers: "is it failing at input, parsing, validation, or integration?" In multi-step protocols (QR codes, network requests, file formats, payment standards) this single clarifying question collapses 5+ debug turns into 2. Don't assume rendering issues when the user reports invalid output — the upstream protocol/payload may be the problem.
3. **Reproduce consistently** — can you trigger it reliably? What are the exact steps? If not reproducible, gather more data instead of guessing.
4. **Check recent changes** — what changed that could cause this? Git diff, recent commits, new dependencies, config changes.
5. **Trace data flow** — where does the bad value originate? What called this with the wrong input? Keep tracing upstream until you find the source. Fix at the source, not at the symptom.

In multi-component systems, add diagnostic instrumentation at each component boundary before proposing fixes. Run once to gather evidence showing WHERE it breaks, then investigate that specific component.

### Phase 2: Pattern Analysis

1. **Find working examples** — locate similar working code in the same codebase
2. **Compare against references** — if implementing a pattern, read the reference implementation completely
3. **Identify differences** — list every difference between working and broken, however small
4. **Understand dependencies** — what settings, config, environment does this need?

### Phase 3: Hypothesis and Testing

1. **Form a single hypothesis** — state clearly: "I think X is the root cause because Y"
2. **Test minimally** — make the smallest possible change to test the hypothesis. One variable at a time.
3. **Verify** — did it work? Yes: proceed to Phase 4. No: form a new hypothesis. Don't add more fixes on top.

### Phase 4: Implementation

1. **Create a failing test** — simplest possible reproduction. Use TestDrivenDevelopment.
2. **Implement a single fix** — address the root cause, not the symptom. One change at a time.
3. **Verify the fix** — test passes? No other tests broken? Issue actually resolved? Use VerifyCompletion.

### When 3+ Fixes Fail

If three or more fix attempts have failed, stop fixing. This is an architectural problem, not a bug:
- Each fix reveals new shared state or coupling
- Fixes require "massive refactoring"
- Each fix creates new symptoms elsewhere

Discuss with the user before attempting more fixes. Question whether the pattern is fundamentally sound.

## Red Flags

| Thought                                             | Reality                                                        |
| --------------------------------------------------- | -------------------------------------------------------------- |
| "Quick fix for now, investigate later"              | Later never comes. Root cause first.                           |
| "Just try changing X and see if it works"           | That's guessing, not debugging. Form a hypothesis first.       |
| "I don't fully understand but this might work"      | Partial understanding guarantees partial fixes.                |
| "It's probably X, let me fix that"                  | "Probably" is not root cause. Verify before fixing.            |
| "I'll skip the test, I'll manually verify"          | Manual verification doesn't prevent regressions.              |
| "One more fix attempt"                              | After 2+ failures, question the architecture instead.          |
| "Pattern says X but I'll adapt it differently"      | Read the reference completely. Adaptation without understanding creates bugs. |
| "Here are the problems:" (lists fixes without investigation) | Listing fixes before investigating is guessing with confidence. |

## Constraints

- No fixes without completing Phase 1
- One hypothesis at a time — never bundle multiple fixes
- If 3+ fixes fail, stop and discuss architecture with the user
- Always create a failing test before implementing a fix
- Say "I don't understand X" when you don't — never pretend


## Additional references

@ConditionBasedWaiting.md
@RootCauseTracing.md
@DefenseInDepth.md
@TestAcademic.md
@TestPressure1.md
@TestPressure2.md
@TestPressure3.md
