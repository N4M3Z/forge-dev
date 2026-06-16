---
name: PullRequest
version: 0.1.0
description: "Manage the pull request lifecycle: author the body to the house standard, create via gh or glab, retrieve and address feedback, retarget stacked PRs, merge and clean up. USE WHEN create a PR, open a pull request, draft a PR, write a PR body, PR description, address PR feedback, PR comments, retarget a stacked PR, PR merged but changes missing from main, merge a PR. For the merge-vs-PR-vs-discard decision use FinishBranch; for processing review feedback rigor use ReceiveReview; for authoring the review-request message use RequestReview."
allowed-tools: Read, Write, Bash
---

# PullRequest

Drive a pull request from branch to merge with platform-native CLIs (`gh`, `glab`). The body is the product: it explains the why before the what in as few sentences as possible, because the diff already shows the code.

## Workflow

### Step 1: Preflight

Work must sit on a feature branch; if on the default branch, branch first. Confirm the changeset is committed and validation passes. If the question is still "merge locally, PR, or discard?", that decision belongs to FinishBranch, not here.

### Step 2: Discovery

Check `gh pr list` (or `glab mr list`) before creating anything: a PR may already exist for the branch or the work may duplicate an open one. If one exists, switch to updating it and retrieving feedback instead of creating a duplicate.

### Step 3: Author the body

Title states what changed, not why it was discovered, in conventional commit form (`type: description`, lowercase, no scope, no trailing period). Body sections in order, omitting any that add nothing:

1. **## Problem**: what does not work, from the user's or operator's perspective. Include the failing invocation, error message, or surprising output. For features, name the missing capability.
2. **## Fix** (or **## Approach** for features): what changes, in prose. Never duplicate the diff.
3. **## Out of scope**: what is deliberately not changed. Omit when obvious.
4. **## Test plan**: markdown task list, `- [x]` completed and `- [ ]` pending, citing the commands run.

Link the closing issue with `Closes #NN` at the top. Pure chores (version bumps, lockfile updates) need only Problem and Test plan. One-sentence sections beat padded ones; bulleted "Summary" lists and prose that paraphrases the diff are forbidden.

Write the body to a temp file with the Write tool and pass `--body-file`; never compose it inline with heredoc.

### Step 4: Create

```sh
git push -u origin <branch>
gh pr create --title "<type>: <description>" --body-file <tmpfile>
```

GitLab: `glab mr create --title "<type>: <description>" --description "$(cat <tmpfile>)"` (glab has no file-reading description flag).

### Step 5: Feedback

When told there is feedback, fetch it before asking anything: `gh pr view --comments` (or `--web` for inline threads). Process suggestions with ReceiveReview rigor: verify before implementing, push back when wrong.

### Step 6: Merge and clean up

Gate on CI first: `gh pr checks <num> --watch`. On failure, route to FixCI before anything else.

Merge with `gh pr merge --squash --delete-branch` (GitLab: `glab mr merge --squash --remove-source-branch`); the platform squash collapses fix/chore/test commits into the feature, so main reads as a sequence of features. Squash locally first only when the PR will be merge-committed instead. After a squash-merge, delete the local branch with `git branch -D` (the squash commit means no merge ancestry).

## Stacked PRs

A child PR targeting a parent feature branch does not cascade to main when the parent merges. Squash-merging the parent creates a new commit on main and leaves the parent branch divergent; the child then merges into that divergent branch and its content never reaches main while GitHub shows it "merged". Retarget the child to main as soon as the parent merges.

## Red Flags

| Thought                                  | Reality                                                                  |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| "Heredoc the body into gh pr create"     | Write the body to a file, pass --body-file. Heredocs hide the diff.      |
| "Add a Summary section with bullets"     | Forbidden. Problem and Fix prose carry the why; the diff shows the what. |
| "Describe the code changes in the body"  | The diff already shows the code. The body explains why.                  |
| "Child PR shows merged, work is done"    | Squash-merged parents orphan children. Retarget to main and verify.      |
| "Create the PR from the default branch"  | Branch first. PRs from main break the merge target.                      |

## Constraints

- Platform-native CLIs (`gh`, `glab`) for the entire lifecycle, never web-only flows
- Title and commits follow conventional commit form
- Never attribute content to agents, councils, or reviews in the body
- A PR is created or merged only on explicit instruction, never proactively
