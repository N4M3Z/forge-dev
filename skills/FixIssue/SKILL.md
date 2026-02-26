---
name: FixIssue
version: 0.1.0
description: Fix issues end-to-end — triage, diagnose, branch, fix, PR/MR, close. Supports GitHub (gh) and GitLab (glab) with cross-repo fixes and submodule bumps. USE WHEN fix issue, github issue, gitlab issue, bug report, fix bug, resolve issue, triage issue, gh issue, fix #.
---

# FixIssue

Fix an issue from triage to close. Platform-agnostic workflow with platform-specific CLI companions.

## Platform Routing

| Platform | CLI | Companion | Detect by |
|----------|-----|-----------|-----------|
| GitHub | `gh` | @GitHub.md | `github.com` in URL or `gh` origin |
| GitLab | `glab` | @GitLab.md | `gitlab.com` in URL or `glab` origin |

Auto-detect from the issue URL or remote origin. If ambiguous, ask the user.

## Input Formats

| Format | Example |
|--------|---------|
| `owner/repo#N` | `N4M3Z/forge-council#8` |
| Issue URL (GitHub) | `https://github.com/N4M3Z/forge-council/issues/8` |
| Issue URL (GitLab) | `https://gitlab.com/group/project/-/issues/42` |
| `#N` (current repo) | `#8` |

## Cross-Repo Topology

When fixing issues in multi-repo or submodule projects, the fix often lives in a different repo than the issue.

| Symptom location | Typical fix location | Pattern |
|-----------------|---------------------|---------|
| Consumer module | Shared library | Fix in lib, bump submodule in consumer |
| Module install/verify fails | Same module | Makefile, config, or stale submodule pointer |
| Skill broken across providers | Same module | SKILL.md content or SKILL.yaml metadata |
| Standalone plugin | Corresponding source module | Fix in source, then sync to standalone |

## Branch Naming

| Type | Branch name |
|------|-------------|
| Bug fix | `fix/<slug>` |
| Feature request | `feat/<slug>` |
| Documentation | `docs/<slug>` |

Slug: lowercase, hyphenated, derived from issue title. Keep under 50 characters.

## Workflow

### Fetch and parse the issue

Read the issue using the platform CLI. Extract:
- **Title** and **body** — the problem statement and reproduction steps
- **Comments** — community analysis, proposed patches, linked PRs/MRs
- **Labels** — severity, affected area
- **State** — confirm it's open (do not fix closed issues without asking)

See the platform companion for exact commands.

### Check existing work

Before starting, check for open PRs/MRs that reference this issue and whether someone is assigned. If work exists, report to the user and ask whether to proceed, contribute, or stop.

### Classify the fix

Determine:

1. **Fix location** — same repo, different repo (cross-repo), or submodule pointer bump
2. **Scope** — single file, multi-file, multi-module
3. **Dependencies** — does the fix require changes in a shared library first?

Use the [Cross-Repo Topology](#cross-repo-topology) table. For submodule-related failures, check the submodule pointer:

```bash
git -C REPO_PATH submodule status lib
```

### Create a linked branch

Use the platform CLI to create a branch linked to the issue. See the platform companion for commands.

If the fix is cross-repo, create the branch in the fix repo, not the issue repo.

Fallback (any platform):

```bash
git checkout -b fix/<slug>
```

### Diagnose and fix

Read the relevant code. Identify the root cause. Implement the fix.

**If cross-repo fix:**
1. Fix in the dependency repo first
2. Run tests in the dependency repo
3. Commit and push the fix
4. Bump the submodule pointer in the consumer repo
5. Verify the consumer repo builds and tests pass

**Testing checklist:**
- Run existing tests: `cargo test` / `make test` / project-specific runner
- Add regression test coverage for the bug
- Run linting: `cargo clippy` / `make lint`
- If build/install issue: `make install && make verify`

### Create the PR / MR

Use the platform CLI to create a PR (GitHub) or MR (GitLab) with:
- Conventional commit prefix in the title (`fix:`, `feat:`, `docs:`)
- Cross-repo reference in the body (creates a visible link)
- Test plan checklist

See the platform companion for exact templates and auto-close keywords.

**Submodule bump** (after fix PR/MR merges in dependency):

```bash
git -C path/to/submodule checkout main && git -C path/to/submodule pull
git add path/to/submodule
git commit -m "chore: bump <submodule> for fix #N"
```

### Close cross-repo issues

Same-repo: auto-closes via keywords in the PR/MR body.

Cross-repo: auto-close does NOT work. Manually close with a comment linking to the fix. See the platform companion for the close command.

### Report

Summarize:
- **Issue**: owner/repo#N — title
- **Platform**: GitHub / GitLab
- **Fix**: owner/fix-repo#PR — what changed
- **Cross-repo**: yes/no — manual close performed if yes
- **Submodule bump**: yes/no — bump commit/PR created if yes
- **Tests**: passing/failing

## ReviewComment

Before posting any public-facing message via the platform CLI, use **AskUserQuestion** to show the draft message and get user approval. This applies to:

- Issue close comments (`gh issue close -c`, `glab issue close -c`)
- PR/MR body text (`gh pr create --body`, `glab mr create --description`)
- Issue comments (`gh issue comment`, `glab issue note`)

Present the message as a preview option so the user can approve, edit, or reject it. Never post public messages without confirmation.

## Constraints

- Always check for existing PRs/MRs and assignees before starting work
- Never fix closed issues without asking the user
- Cross-repo auto-close does not work on either platform — always close manually
- Submodule bumps are separate commits
- Follow the /Git skill conventions for commit messages and staging
- If the issue is a feature request (not a bug), confirm scope with the user before implementing
- **ReviewComment**: always confirm public messages before posting (see above)
- For GitHub operations beyond the issue→PR workflow (releases, Actions, repo settings), see /GitHub
