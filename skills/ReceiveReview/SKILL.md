---
name: ReceiveReview
version: 0.1.0
description: "Process code review feedback with technical rigor — verify before implementing, push back when wrong. USE WHEN receiving code review feedback, before implementing review suggestions."
---

# ReceiveReview

Process code review feedback critically. Verify suggestions are correct before implementing. Push back when they're wrong. Never performatively agree.

1. **Read all feedback first** — read every comment before implementing any change. Understand the full picture before acting.
2. **Categorize** — sort into blocking (must fix), important (should fix), suggestions (could fix)
3. **Verify each suggestion** — read the code the reviewer references. Is their understanding correct? Does their suggestion actually improve the code?
4. **Evaluate** — for each suggestion:
    - Correct and valuable: implement it
    - Correct but YAGNI: push back with reasoning
    - Incorrect: push back with technical evidence
    - Unclear: ask for clarification instead of guessing
5. **Implement in order** — blocking issues first, then simple fixes, then complex changes
6. **Report** — summarize what was implemented, what was pushed back on and why

## Responding to Feedback

Forbidden responses: "You're absolutely right!", "Great point!", "Thanks for catching that!" — these are performative, not technical. Respond with what you did and why.

When pushing back, provide technical reasoning:
- "This would add a dependency we don't need because X"
- "The current pattern handles this case via Y — changing it would break Z"
- "This suggestion addresses a scenario that can't occur because of the guard at line N"

When the reviewer is right, just fix it. No performance needed.

## Red Flags

| Thought                                        | Reality                                                        |
| ---------------------------------------------- | -------------------------------------------------------------- |
| "They're probably right, I'll just do it"      | Verify first. Reviewers have limited context.                  |
| "I don't agree but I'll do it anyway"          | Push back with evidence. Silent compliance ships bad code.     |
| "Let me add this feature they suggested"       | YAGNI check. Is it in the spec? Is it needed?                  |
| "I'll implement all suggestions at once"       | One at a time, in priority order. Batching hides interactions. |
| "Great point!" (about to implement blindly)    | Read the code. Is it actually a great point?                   |
| "This feedback is wrong, I'll ignore it"       | Respond with reasoning. Ignoring erodes trust.                 |

## Constraints

- Read all feedback before implementing any change
- Never performatively agree — respond with technical substance
- Verify each suggestion against the actual code before implementing
- Push back with evidence when a suggestion is wrong or unnecessary
- Implement in priority order: blocking, then simple, then complex
- Ask for clarification on unclear feedback instead of guessing intent


## Additional references

@ReceivingCodeReview.md
